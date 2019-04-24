# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""
Models de l'application users.

On défini ici des models django classiques:
- users, qui hérite de l'abstract base user de django. Permet de définit
un utilisateur du site (login, passwd, chambre, adresse, etc)
- les whiteslist
- les bannissements
- les établissements d'enseignement (school)
- les droits (right et listright)
- les utilisateurs de service (pour connexion automatique)

On défini aussi des models qui héritent de django-ldapdb :
- ldapuser
- ldapgroup
- ldapserviceuser

Ces utilisateurs ldap sont synchronisés à partir des objets
models sql classiques. Seuls certains champs essentiels sont
dupliqués.
"""


from __future__ import unicode_literals

import re
import uuid
import datetime
import sys

from django.db import models
from django.db.models import Q
from django import forms
from django.forms import ValidationError
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.template import Context, loader
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group
)
from django.core.validators import RegexValidator
import traceback
from django.utils.translation import ugettext_lazy as _

from reversion import revisions as reversion

import ldapdb.models
import ldapdb.models.fields

from re2o.settings import LDAP, GID_RANGES, UID_RANGES
from re2o.field_permissions import FieldPermissionModelMixin
from re2o.mixins import AclMixin, RevMixin
from re2o.base import smtp_check

from cotisations.models import Cotisation, Facture, Paiement, Vente
from machines.models import Domain, Interface, Machine, regen
from preferences.models import GeneralOption, AssoOption, OptionalUser
from preferences.models import OptionalMachine, MailMessageOption


# Utilitaires généraux


def linux_user_check(login):
    """ Validation du username pour respecter les contraintes unix"""
    UNIX_LOGIN_PATTERN = re.compile("^[a-z][a-z0-9-]*[$]?$")
    return UNIX_LOGIN_PATTERN.match(login)


def linux_user_validator(login):
    """ Retourne une erreur de validation si le login ne respecte
    pas les contraintes unix (maj, min, chiffres ou tiret)"""
    if not linux_user_check(login):
        raise forms.ValidationError(
            _("The username '%(label)s' contains forbidden characters."),
            params={'label': login},
        )


def get_fresh_user_uid():
    """ Renvoie le plus petit uid non pris. Fonction très paresseuse """
    uids = list(range(
        int(min(UID_RANGES['users'])),
        int(max(UID_RANGES['users']))
    ))
    try:
        used_uids = list(User.objects.values_list('uid_number', flat=True))
    except:
        used_uids = []
    free_uids = [id for id in uids if id not in used_uids]
    return min(free_uids)


def get_fresh_gid():
    """ Renvoie le plus petit gid libre  """
    gids = list(range(
        int(min(GID_RANGES['posix'])),
        int(max(GID_RANGES['posix']))
    ))
    used_gids = list(ListRight.objects.values_list('gid', flat=True))
    free_gids = [id for id in gids if id not in used_gids]
    return min(free_gids)


class UserManager(BaseUserManager):
    """User manager basique de django"""

    def _create_user(
            self,
            username,
            surname,
            email,
            password=None,
            su=False
    ):
        if not username:
            raise ValueError(_("Users must have an username."))

        if not linux_user_check(username):
            raise ValueError(_("Username should only contain [a-z0-9-]."))

        user = Adherent(
            username=username,
            surname=surname,
            name=surname,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        if su:
            user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_user(self, username, surname, email, password=None):
        """
        Creates and saves a User with the given username, name, surname, email,
        and password.
        """
        return self._create_user(username, surname, email, password, False)

    def create_superuser(self, username, surname, email, password):
        """
        Creates and saves a superuser with the given username, name, surname,
        email, and password.
        """
        return self._create_user(username, surname, email, password, True)


class User(RevMixin, FieldPermissionModelMixin, AbstractBaseUser,
           PermissionsMixin, AclMixin):
    """ Definition de l'utilisateur de base.
    Champs principaux : name, surnname, username, email, room, password
    Herite du django BaseUser et du système d'auth django"""

    STATE_ACTIVE = 0
    STATE_DISABLED = 1
    STATE_ARCHIVE = 2
    STATE_NOT_YET_ACTIVE = 3
    STATE_FULL_ARCHIVE = 4
    STATES = (
        (0, _("Active")),
        (1, _("Disabled")),
        (2, _("Archived")),
        (3, _("Not yet active")),
        (4, _("Full Archived")),
    )

    surname = models.CharField(max_length=255)
    username = models.CharField(
        max_length=32,
        unique=True,
        help_text=_("Must only contain letters, numerals or dashes."),
        validators=[linux_user_validator]
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text=_("External email address allowing us to contact you.")
    )
    local_email_redirect = models.BooleanField(
        default=False,
        help_text=_("Enable redirection of the local email messages to the"
                    " main email address.")
    )
    local_email_enabled = models.BooleanField(
        default=False,
        help_text=_("Enable the local email account.")
    )
    school = models.ForeignKey(
        'School',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    shell = models.ForeignKey(
        'ListShell',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    comment = models.CharField(
        help_text=_("Comment, school year"),
        max_length=255,
        blank=True
    )
    pwd_ntlm = models.CharField(max_length=255)
    state = models.IntegerField(choices=STATES, default=STATE_NOT_YET_ACTIVE)
    registered = models.DateTimeField(auto_now_add=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    uid_number = models.PositiveIntegerField(
        default=get_fresh_user_uid,
        unique=True
    )
    rezo_rez_uid = models.PositiveIntegerField(
        unique=True,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'This is updated depending on the state of the user.'
        ),
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['surname', 'email']

    objects = UserManager()

    class Meta:
        permissions = (
            ("change_user_password",
             _("Can change the password of a user")),
            ("change_user_state", _("Can edit the state of a user")),
            ("change_user_force", _("Can force the move")),
            ("change_user_shell", _("Can edit the shell of a user")),
            ("change_user_groups",
             _("Can edit the groups of rights of a user (critical"
               " permission)")),
            ("change_all_users",
             _("Can edit all users, including those with rights.")),
        )
        verbose_name = _("user (member or club)")
        verbose_name_plural = _("users (members or clubs)")

    @cached_property
    def name(self):
        """Si il s'agit d'un adhérent, on renvoie le prénom"""
        if self.is_class_adherent:
            return self.adherent.name
        else:
            return ''

    @cached_property
    def room(self):
        """Alias vers room """
        if self.is_class_adherent:
            return self.adherent.room
        elif self.is_class_club:
            return self.club.room
        else:
            raise NotImplementedError(_("Unknown type."))

    @cached_property
    def get_mail_addresses(self):
        if self.local_email_enabled:
            return self.emailaddress_set.all()
        return None

    @cached_property
    def get_mail(self):
        """Return the mail address choosen by the user"""
        if not OptionalUser.get_cached_value('local_email_accounts_enabled') or not self.local_email_enabled or self.local_email_redirect:
            return str(self.email)
        else:
            return str(self.emailaddress_set.get(local_part=self.username.lower()))

    @cached_property
    def class_name(self):
        """Renvoie si il s'agit d'un adhérent ou d'un club"""
        if hasattr(self, 'adherent'):
            return _("Member")
        elif hasattr(self, 'club'):
            return _("Club")
        else:
            raise NotImplementedError(_("Unknown type."))

    @cached_property
    def gid_number(self):
        """renvoie le gid par défaut des users"""
        return int(LDAP['user_gid'])

    @cached_property
    def is_class_club(self):
        """ Returns True if the object is a Club (subclassing User) """
        # TODO : change to isinstance (cleaner)
        return hasattr(self, 'club')

    @cached_property
    def is_class_adherent(self):
        """ Returns True if the object is a Adherent (subclassing User) """
        # TODO : change to isinstance (cleaner)
        return hasattr(self, 'adherent')

    def set_active(self):
        """Enable this user if he subscribed successfully one time before
        Reenable it if it was archived
        Do nothing if disabed"""
        if self.state == self.STATE_NOT_YET_ACTIVE:
            if self.facture_set.filter(valid=True).filter(Q(vente__type_cotisation='All') | Q(vente__type_cotisation='Adhesion')).exists() or OptionalUser.get_cached_value('all_users_active'):
                self.state = self.STATE_ACTIVE
                self.save()
        if self.state == self.STATE_ARCHIVE or self.state == self.STATE_FULL_ARCHIVE:
            self.state = self.STATE_ACTIVE
            self.unarchive()
            self.save()

    @property
    def is_staff(self):
        """ Fonction de base django, renvoie si l'user est admin"""
        return self.is_admin

    @property
    def is_admin(self):
        """ Renvoie si l'user est admin"""
        admin, _ = Group.objects.get_or_create(name="admin")
        return self.is_superuser or admin in self.groups.all()

    def get_full_name(self):
        """ Renvoie le nom complet de l'user formaté nom/prénom"""
        name = self.name
        if name:
            return "%s %s" % (name, self.surname)
        else:
            return self.surname

    def get_short_name(self):
        """ Renvoie seulement le nom"""
        return self.surname

    @cached_property
    def gid(self):
        """return the default gid of user"""
        return LDAP['user_gid']

    @property
    def get_shell(self):
        """ A utiliser de préférence, prend le shell par défaut
        si il n'est pas défini"""
        return self.shell or OptionalUser.get_cached_value('shell_default')

    @cached_property
    def home_directory(self):
        return '/home/' + self.username

    @cached_property
    def get_shadow_expire(self):
        """Return the shadow_expire value for the user"""
        if self.state == self.STATE_DISABLED:
            return str(0)
        else:
            return None

    def end_adhesion(self):
        """ Renvoie la date de fin d'adhésion d'un user. Examine les objets
        cotisation"""
        date_max = Cotisation.objects.filter(
            vente__in=Vente.objects.filter(
                facture__in=Facture.objects.filter(
                    user=self
                ).exclude(valid=False)
            )
        ).filter(
            Q(type_cotisation='All') | Q(type_cotisation='Adhesion')
        ).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    def end_connexion(self):
        """ Renvoie la date de fin de connexion d'un user. Examine les objets
        cotisation"""
        date_max = Cotisation.objects.filter(
            vente__in=Vente.objects.filter(
                facture__in=Facture.objects.filter(
                    user=self
                ).exclude(valid=False)
            )
        ).filter(
            Q(type_cotisation='All') | Q(type_cotisation='Connexion')
        ).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    def is_adherent(self):
        """ Renvoie True si l'user est adhérent : si
        self.end_adhesion()>now"""
        end = self.end_adhesion()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True

    def is_connected(self):
        """ Renvoie True si l'user est adhérent : si
        self.end_adhesion()>now et end_connexion>now"""
        end = self.end_connexion()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return self.is_adherent()

    def end_ban(self):
        """ Renvoie la date de fin de ban d'un user, False sinon """
        date_max = Ban.objects.filter(
            user=self
        ).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    def end_whitelist(self):
        """ Renvoie la date de fin de whitelist d'un user, False sinon """
        date_max = Whitelist.objects.filter(
            user=self
        ).aggregate(models.Max('date_end'))['date_end__max']
        return date_max

    def is_ban(self):
        """ Renvoie si un user est banni ou non """
        end = self.end_ban()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True

    def is_whitelisted(self):
        """ Renvoie si un user est whitelisté ou non """
        end = self.end_whitelist()
        if not end:
            return False
        elif end < timezone.now():
            return False
        else:
            return True

    def has_access(self):
        """ Renvoie si un utilisateur a accès à internet """
        return (self.state == User.STATE_ACTIVE and
                not self.is_ban() and
                (self.is_connected() or self.is_whitelisted())) \
                or self == AssoOption.get_cached_value('utilisateur_asso')

    def end_access(self):
        """ Renvoie la date de fin normale d'accès (adhésion ou whiteliste)"""
        if not self.end_connexion():
            if not self.end_whitelist():
                return None
            else:
                return self.end_whitelist()
        else:
            if not self.end_whitelist():
                return self.end_connexion()
            else:
                return max(self.end_connexion(), self.end_whitelist())

    @cached_property
    def solde(self):
        """ Renvoie le solde d'un user.
        Somme les crédits de solde et retire les débit payés par solde"""
        solde_objects = Paiement.objects.filter(is_balance=True)
        somme_debit = Vente.objects.filter(
            facture__in=Facture.objects.filter(
                user=self,
                paiement__in=solde_objects,
                valid=True
            )
        ).aggregate(
            total=models.Sum(
                models.F('prix')*models.F('number'),
                output_field=models.DecimalField()
            )
        )['total'] or 0
        somme_credit = Vente.objects.filter(
            facture__in=Facture.objects.filter(user=self, valid=True),
            name='solde'
        ).aggregate(
            total=models.Sum(
                models.F('prix')*models.F('number'),
                output_field=models.DecimalField()
            )
        )['total'] or 0
        return somme_credit - somme_debit

    @classmethod
    def users_interfaces(cls, users, active=True, all_interfaces=False):
        """ Renvoie toutes les interfaces dont les machines appartiennent à
        self. Par defaut ne prend que les interfaces actives"""
        if all_interfaces:
            return Interface.objects.filter(
                machine__in=Machine.objects.filter(user__in=users)
            ).select_related('domain__extension')
        else:
            return Interface.objects.filter(
                machine__in=Machine.objects.filter(user__in=users, active=active)
            ).select_related('domain__extension')

    def user_interfaces(self, active=True, all_interfaces=False):
        """ Renvoie toutes les interfaces dont les machines appartiennent à
        self. Par defaut ne prend que les interfaces actives"""
        return self.users_interfaces([self], active=active, all_interfaces=all_interfaces)

    def assign_ips(self):
        """ Assign une ipv4 aux machines d'un user """
        interfaces = self.user_interfaces()
        with transaction.atomic(), reversion.create_revision():
            Interface.mass_assign_ipv4(interfaces)
            reversion.set_comment(_("IPv4 assigning"))

    def unassign_ips(self):
        """ Désassigne les ipv4 aux machines de l'user"""
        interfaces = self.user_interfaces()
        with transaction.atomic(), reversion.create_revision():
            Interface.mass_unassign_ipv4(interfaces)
            reversion.set_comment(_("IPv4 unassigning"))

    @classmethod
    def mass_unassign_ips(cls, users_list):
        interfaces = cls.users_interfaces(users_list)
        with transaction.atomic(), reversion.create_revision():
            Interface.mass_unassign_ipv4(interfaces)
            reversion.set_comment(_("IPv4 assigning"))

    @classmethod
    def mass_disable_email(cls, queryset_users):
        """Disable email account and redirection"""
        queryset_users.update(local_email_enabled=False)
        queryset_users.update(local_email_redirect=False)

    @classmethod
    def mass_delete_data(cls, queryset_users):
        """This users will be completely archived, so only keep mandatory data"""
        cls.mass_disable_email(queryset_users)
        Machine.mass_delete(Machine.objects.filter(user__in=queryset_users))
        cls.ldap_delete_users(queryset_users)

    def disable_email(self):
        """Disable email account and redirection"""
        self.local_email_enabled=False
        self.local_email_redirect=False

    def delete_data(self):
        """This user will be completely archived, so only keep mandatory data"""
        self.disable_email()
        self.machine_set.all().delete()

    @classmethod
    def mass_archive(cls, users_list):
        """Mass Archive several users, take a queryset
        Copy Queryset to avoid eval problem with queryset update"""
        #Force eval of queryset
        bool(users_list)
        users_list = users_list.all()
        cls.mass_unassign_ips(users_list)
        users_list.update(state=User.STATE_ARCHIVE)

    @classmethod
    def mass_full_archive(cls, users_list):
        """Mass Archive several users, take a queryset
        Copy Queryset to avoid eval problem with queryset update"""
        #Force eval of queryset
        bool(users_list)
        users_list = users_list.all()
        cls.mass_unassign_ips(users_list)
        cls.mass_delete_data(users_list)
        users_list.update(state=User.STATE_FULL_ARCHIVE)

    def archive(self):
        """ Filling the user; no more active"""
        self.unassign_ips()

    def full_archive(self):
        """Full Archive = Archive + Service access complete deletion"""
        self.archive()
        self.delete_data()
        self.ldap_del()

    def unarchive(self):
        """Unfilling the user"""
        self.assign_ips()
        self.ldap_sync()

    def state_sync(self):
        """Archive, or unarchive, if the user was not active/or archived before"""
        if self.__original_state != self.STATE_ACTIVE  and self.state == self.STATE_ACTIVE:
            self.unarchive()
        elif self.__original_state != self.STATE_ARCHIVE and self.state == self.STATE_ARCHIVE:
            self.archive()
        elif self.__original_state != self.STATE_FULL_ARCHIVE and self.state == self.STATE_FULL_ARCHIVE:
            self.full_archive()

    def ldap_sync(self, base=True, access_refresh=True, mac_refresh=True,
                  group_refresh=False):
        """ Synchronisation du ldap. Synchronise dans le ldap les attributs de
        self
        Options : base : synchronise tous les attributs de base - nom, prenom,
        mail, password, shell, home
        access_refresh : synchronise le dialup_access notant si l'user a accès
        aux services
        mac_refresh : synchronise les machines de l'user
        group_refresh : synchronise les group de l'user
        Si l'instance n'existe pas, on crée le ldapuser correspondant"""
        if sys.version_info[0] >= 3 and (self.state == self.STATE_ACTIVE or self.state == self.STATE_ARCHIVE or self.state == self.STATE_DISABLED):
            self.refresh_from_db()
            try:
                user_ldap = LdapUser.objects.get(uidNumber=self.uid_number)
            except LdapUser.DoesNotExist:
                user_ldap = LdapUser(uidNumber=self.uid_number)
                base = True
                access_refresh = True
                mac_refresh = True
            if base:
                user_ldap.name = self.username
                user_ldap.sn = self.username
                user_ldap.dialupAccess = str(self.has_access())
                user_ldap.home_directory = self.home_directory
                user_ldap.mail = self.get_mail
                user_ldap.given_name = self.surname.lower() + '_'\
                    + self.name.lower()[:3]
                user_ldap.gid = LDAP['user_gid']
                if '{SSHA}' in self.password or '{SMD5}' in self.password:
                    # We remove the extra $ added at import from ldap
                    user_ldap.user_password = self.password[:6] + \
                        self.password[7:]
                elif '{crypt}' in self.password:
                    # depending on the length, we need to remove or not a $
                    if len(self.password) == 41:
                        user_ldap.user_password = self.password
                    else:
                        user_ldap.user_password = self.password[:7] + \
                            self.password[8:]

                user_ldap.sambat_nt_password = self.pwd_ntlm.upper()
                if self.get_shell:
                    user_ldap.login_shell = str(self.get_shell)
                user_ldap.shadowexpire = self.get_shadow_expire
            if access_refresh:
                user_ldap.dialupAccess = str(self.has_access())
            if mac_refresh:
                user_ldap.macs = [str(mac) for mac in Interface.objects.filter(
                    machine__user=self
                ).values_list('mac_address', flat=True).distinct()]
            if group_refresh:
                # Need to refresh all groups because we don't know which groups
                # were updated during edition of groups and the user may no longer
                # be part of the updated group (case of group removal)
                for group in Group.objects.all():
                    if hasattr(group, 'listright'):
                        group.listright.ldap_sync()
            user_ldap.save()

    def ldap_del(self):
        """ Supprime la version ldap de l'user"""
        try:
            user_ldap = LdapUser.objects.get(name=self.username)
            user_ldap.delete()
        except LdapUser.DoesNotExist:
            pass

    @classmethod
    def ldap_delete_users(cls, queryset_users):
        """Delete multiple users in ldap"""
        LdapUser.objects.filter(name__in=list(queryset_users.values_list('username', flat=True)))

    def notif_inscription(self):
        """ Prend en argument un objet user, envoie un mail de bienvenue """
        template = loader.get_template('users/email_welcome')
        mailmessageoptions, _created = MailMessageOption\
            .objects.get_or_create()
        context = {
            'nom': self.get_full_name(),
            'asso_name': AssoOption.get_cached_value('name'),
            'asso_email': AssoOption.get_cached_value('contact'),
            'welcome_mail_fr': mailmessageoptions.welcome_mail_fr,
            'welcome_mail_en': mailmessageoptions.welcome_mail_en,
            'username': self.username,
        }
        send_mail(
            'Bienvenue au %(name)s / Welcome to %(name)s' % {
                'name': AssoOption.get_cached_value('name')
            },
            '',
            GeneralOption.get_cached_value('email_from'),
            [self.email],
            html_message=template.render(context)
        )
        return

    def autoregister_machine(self, mac_address, nas_type):
        """ Fonction appellée par freeradius. Enregistre la mac pour
        une machine inconnue sur le compte de l'user"""
        allowed, _message = Machine.can_create(self, self.id)
        if not allowed:
            return False, _("Maximum number of registered machines reached.")
        if not nas_type:
            return False, _("Re2o doesn't know wich machine type to assign.")
        machine_type_cible = nas_type.machine_type
        try:
            machine_parent = Machine()
            machine_parent.user = self
            interface_cible = Interface()
            interface_cible.mac_address = mac_address
            interface_cible.type = machine_type_cible
            interface_cible.clean()
            machine_parent.clean()
            domain = Domain()
            domain.name = self.get_next_domain_name()
            domain.interface_parent = interface_cible
            domain.clean()
            machine_parent.save()
            interface_cible.machine = machine_parent
            interface_cible.save()
            domain.interface_parent = interface_cible
            domain.clean()
            domain.save()
            self.notif_auto_newmachine(interface_cible)
        except Exception as error:
            return False,  traceback.format_exc()
        return interface_cible, _("OK")

    def notif_auto_newmachine(self, interface):
        """Notification mail lorsque une machine est automatiquement
        ajoutée par le radius"""
        template = loader.get_template('users/email_auto_newmachine')
        context = {
            'nom': self.get_full_name(),
            'mac_address': interface.mac_address,
            'asso_name': AssoOption.get_cached_value('name'),
            'interface_name': interface.domain,
            'asso_email': AssoOption.get_cached_value('contact'),
            'username': self.username,
        }
        send_mail(
            "Ajout automatique d'une machine / New machine autoregistered",
            '',
            GeneralOption.get_cached_value('email_from'),
            [self.email],
            html_message=template.render(context)
        )
        return

    def set_password(self, password):
        """ A utiliser de préférence, set le password en hash courrant et
        dans la version ntlm"""
        super().set_password(password)
        from re2o.login import hash_nt
        self.pwd_ntlm = hash_nt(password)
        return

    @cached_property
    def email_address(self):
        if (OptionalUser.get_cached_value('local_email_accounts_enabled')
                and self.local_email_enabled):
            return self.emailaddress_set.all()
        return EMailAddress.objects.none()

    def get_next_domain_name(self):
        """Look for an available name for a new interface for
        this user by trying "username0", "username1", "username2", ...

        Recherche un nom disponible, pour une machine. Doit-être
        unique, concatène le nom, le username et le numero de machine
        """

        def simple_username():
            """Renvoie le username sans underscore (compat dns)"""
            return self.username.replace('_', '-').lower()

        def composed_username(name):
            """Renvoie le resultat de simpleusername et rajoute le nom"""
            return simple_username() + str(name)

        num = 0
        while Domain.objects.filter(name=composed_username(num)):
            num += 1
        return composed_username(num)

    def can_edit(self, user_request, *_args, **_kwargs):
        """Check if a user can edit a user object.

        :param self: The user which is to be edited.
        :param user_request: The user who requests to edit self.
        :return: a message and a boolean which is True if self is a club and
            user_request one of its member, or if user_request is self, or if
            user_request has the 'cableur' right.
        """
        if self.is_class_club and user_request.is_class_adherent:
            if (self == user_request or
                    user_request.has_perm('users.change_user') or
                    user_request.adherent in self.club.administrators.all()):
                return True, None
            else:
                return False, _("You don't have the right to edit this club.")
        else:
            if self == user_request:
                return True, None
            elif user_request.has_perm('users.change_all_users'):
                return True, None
            elif user_request.has_perm('users.change_user'):
                if self.groups.filter(listright__critical=True):
                    return False, (_("User with critical rights, can't be"
                                     " edited."))
                elif self == AssoOption.get_cached_value('utilisateur_asso'):
                    return False, (_("Impossible to edit the organisation's"
                                     " user without the 'change_all_users'"
                                     " right."))
                else:
                    return True, None
            elif user_request.has_perm('users.change_all_users'):
                return True, None
            else:
                return False, (_("You don't have the right to edit another"
                                 " user."))

    def can_change_password(self, user_request, *_args, **_kwargs):
        """Check if a user can change a user's password

        :param self: The user which is to be edited
        :param user_request: The user who request to edit self
        :returns: a message and a boolean which is True if self is a club
            and user_request one of it's admins, or if user_request is self,
            or if user_request has the right to change other's password
        """
        if self.is_class_club and user_request.is_class_adherent:
            if (self == user_request or
                    user_request.has_perm('users.change_user_password') or
                    user_request.adherent in self.club.administrators.all()):
                return True, None
            else:
                return False, _("You don't have the right to edit this club.")
        else:
            if (self == user_request or
                    user_request.has_perm('users.change_user_groups')):
                # Peut éditer les groupes d'un user,
                # c'est un privilège élevé, True
                return True, None
            elif (user_request.has_perm('users.change_user') and
                  not self.groups.all()):
                return True, None
            else:
                return False, (_("You don't have the right to edit another"
                                 " user."))

    def check_selfpasswd(self, user_request, *_args, **_kwargs):
        """ Returns (True, None) if user_request is self, else returns
        (False, None)
        """
        return user_request == self, None

    def can_change_room(self, user_request, *_args, **_kwargs):
        """ Check if a user can change a room

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a state
        """
        if not ((self.pk == user_request.pk and OptionalUser.get_cached_value('self_change_room'))
            or user_request.has_perm('users.change_user')):
            return False, _("Permission required to change the room.")
        else:
            return True, None

    @staticmethod
    def can_change_state(user_request, *_args, **_kwargs):
        """ Check if a user can change a state

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a state
        """
        return (
            user_request.has_perm('users.change_user_state'),
            _("Permission required to change the state.")
        )

    def can_change_shell(self, user_request, *_args, **_kwargs):
        """ Check if a user can change a shell

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a shell
        """
        if not ((self.pk == user_request.pk and OptionalUser.get_cached_value('self_change_shell'))
            or user_request.has_perm('users.change_user_shell')):
            return False, _("Permission required to change the shell.")
        else:
            return True, None

    @staticmethod
    def can_change_local_email_redirect(user_request, *_args, **_kwargs):
        """ Check if a user can change local_email_redirect.

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a redirection
        """
        return (
            OptionalUser.get_cached_value('local_email_accounts_enabled'),
            _("Local email accounts must be enabled.")
        )

    @staticmethod
    def can_change_local_email_enabled(user_request, *_args, **_kwargs):
        """ Check if a user can change internal address.

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change internal address
        """
        return (
            OptionalUser.get_cached_value('local_email_accounts_enabled'),
            _("Local email accounts must be enabled.")
        )

    @staticmethod
    def can_change_force(user_request, *_args, **_kwargs):
        """ Check if a user can change a force

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a force
        """
        return (
            user_request.has_perm('users.change_user_force'),
            _("Permission required to force the move.")
        )

    @staticmethod
    def can_change_groups(user_request, *_args, **_kwargs):
        """ Check if a user can change a group

        :param user_request: The user who request
        :returns: a message and a boolean which is True if the user has
        the right to change a group
        """
        return (
            user_request.has_perm('users.change_user_groups'),
            _("Permission required to edit the user's groups of rights.")
        )

    @staticmethod
    def can_change_is_superuser(user_request, *_args, **_kwargs):
        """ Check if an user can change a is_superuser flag

        :param user_request: The user who request
        :returns: a message and a boolean which is True if permission is granted.
        """
        return (
            user_request.is_superuser,
            _("'superuser' right required to edit the superuser flag.")
        )

    def can_view(self, user_request, *_args, **_kwargs):
        """Check if an user can view an user object.

        :param self: The targeted user.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
            text
        """
        if self.is_class_club and user_request.is_class_adherent:
            if (self == user_request or
                    user_request.has_perm('users.view_user') or
                    user_request.adherent in self.club.administrators.all() or
                    user_request.adherent in self.club.members.all()):
                return True, None
            else:
                return False, _("You don't have the right to view this club.")
        else:
            if (self == user_request or
                    user_request.has_perm('users.view_user')):
                return True, None
            else:
                return False, (_("You don't have the right to view another"
                                 " user."))

    @staticmethod
    def can_view_all(user_request, *_args, **_kwargs):
        """Check if an user can access to the list of every user objects

        :param user_request: The user who wants to view the list.
        :return: True if the user can view the list and an explanation
            message.
        """
        return (
            user_request.has_perm('users.view_user'),
            _("You don't have the right to view the list of users.")
        )

    def can_delete(self, user_request, *_args, **_kwargs):
        """Check if an user can delete an user object.

        :param self: The user who is to be deleted.
        :param user_request: The user who requests deletion.
        :return: True if user_request has the right 'bureau', and a
            message.
        """
        return (
            user_request.has_perm('users.delete_user'),
            _("You don't have the right to delete this user.")
        )

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.field_permissions = {
            'shell': self.can_change_shell,
            'force': self.can_change_force,
            'selfpasswd': self.check_selfpasswd,
            'local_email_redirect': self.can_change_local_email_redirect,
            'local_email_enabled': self.can_change_local_email_enabled,
            'room': self.can_change_room,
        }
        self.__original_state = self.state

    def clean(self, *args, **kwargs):
        """Check if this username is already used by any mailalias.
        Better than raising an error in post-save and catching it"""
        if (EMailAddress.objects
            .filter(local_part=self.username.lower()).exclude(user_id=self.id)
            ):
            raise ValidationError(_("This username is already used."))
        if not self.local_email_enabled and not self.email and not (self.state == self.STATE_FULL_ARCHIVE):
            raise ValidationError(_("There is neither a local email address nor an external"
                      " email address for this user.")
            )
        if self.local_email_redirect and not self.email:
            raise ValidationError(_("You can't redirect your local emails if no external email"
                  " address has been set.")
            )

    def save(self, *args, **kwargs):
        self.is_active = (self.state == self.STATE_ACTIVE
                          or self.state == self.STATE_NOT_YET_ACTIVE)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Adherent(User):
    """ A class representing a member (it's a user with special
    informations) """

    name = models.CharField(max_length=255)
    room = models.OneToOneField(
        'topologie.Room',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    gpg_fingerprint = models.CharField(
        max_length=49,
        blank=True,
        null=True,
    )

    class Meta(User.Meta):
        verbose_name = _("member")
        verbose_name_plural = _("members")

    def format_gpgfp(self):
        """Format gpg finger print as AAAA BBBB... from a string AAAABBBB...."""
        self.gpg_fingerprint = ' '.join([self.gpg_fingerprint[i:i + 4] for i in range(0, len(self.gpg_fingerprint), 4)])

    def validate_gpgfp(self):
        """Validate from raw entry if is it a valid gpg fp"""
        if self.gpg_fingerprint:
            gpg_fingerprint = self.gpg_fingerprint.replace(' ', '').upper()
            if not re.match("^[0-9A-F]{40}$", gpg_fingerprint):
                raise ValidationError(_("A GPG fingerprint must contain 40 hexadecimal characters"))
            self.gpg_fingerprint = gpg_fingerprint

    @classmethod
    def get_instance(cls, adherentid, *_args, **_kwargs):
        """Try to find an instance of `Adherent` with the given id.

        :param adherentid: The id of the adherent we are looking for.
        :return: An adherent.
        """
        return cls.objects.get(pk=adherentid)

    @staticmethod
    def can_create(user_request, *_args, **_kwargs):
        """Check if an user can create an user object.

        :param user_request: The user who wants to create a user object.
        :return: a message and a boolean which is True if the user can create
            a user or if the `options.all_can_create` is set.
        """
        if (not user_request.is_authenticated and
                not OptionalUser.get_cached_value('self_adhesion')):
            return False, None
        else:
            if (OptionalUser.get_cached_value('all_can_create_adherent') or
                    OptionalUser.get_cached_value('self_adhesion')):
                return True, None
            else:
                return (
                    user_request.has_perm('users.add_user'),
                    _("You don't have the right to create a user.")
                )

    def clean(self, *args, **kwargs):
        """Format the GPG fingerprint"""
        super(Adherent, self).clean(*args, **kwargs)
        if self.gpg_fingerprint:
            self.validate_gpgfp()
            self.format_gpgfp()


class Club(User):
    """ A class representing a club (it is considered as a user
    with special informations) """

    room = models.ForeignKey(
        'topologie.Room',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    administrators = models.ManyToManyField(
        blank=True,
        to='users.Adherent',
        related_name='club_administrator'
    )
    members = models.ManyToManyField(
        blank=True,
        to='users.Adherent',
        related_name='club_members'
    )
    mailing = models.BooleanField(
        default=False
    )

    class Meta(User.Meta):
        verbose_name = _("club")
        verbose_name_plural = _("clubs")

    @staticmethod
    def can_create(user_request, *_args, **_kwargs):
        """Check if an user can create an user object.

        :param user_request: The user who wants to create a user object.
        :return: a message and a boolean which is True if the user can create
            an user or if the `options.all_can_create` is set.
        """
        if not user_request.is_authenticated:
            return False, None
        else:
            if OptionalUser.get_cached_value('all_can_create_club'):
                return True, None
            else:
                return (
                    user_request.has_perm('users.add_user'),
                    _("You don't have the right to create a club.")
                )

    @staticmethod
    def can_view_all(user_request, *_args, **_kwargs):
        """Check if an user can access to the list of every user objects

        :param user_request: The user who wants to view the list.
        :return: True if the user can view the list and an explanation
            message.
        """
        if user_request.has_perm('users.view_user'):
            return True, None
        if (hasattr(user_request, 'is_class_adherent') and
                user_request.is_class_adherent):
            if (user_request.adherent.club_administrator.all() or
                    user_request.adherent.club_members.all()):
                return True, None
        return False, _("You don't have the right to view the list of users.")

    @classmethod
    def get_instance(cls, clubid, *_args, **_kwargs):
        """Try to find an instance of `Club` with the given id.

        :param clubid: The id of the adherent we are looking for.
        :return: A club.
        """
        return cls.objects.get(pk=clubid)


@receiver(post_save, sender=Adherent)
@receiver(post_save, sender=Club)
@receiver(post_save, sender=User)
def user_post_save(**kwargs):
    """ Synchronisation post_save : envoie le mail de bienvenue si creation
    Synchronise le username, en créant un alias mail correspondant
    Synchronise le ldap"""
    is_created = kwargs['created']
    user = kwargs['instance']
    EMailAddress.objects.get_or_create(
        local_part=user.username.lower(), user=user)
    if is_created:
        user.notif_inscription()
    user.state_sync()
    user.ldap_sync(
        base=True,
        access_refresh=True,
        mac_refresh=False,
        group_refresh=True
    )
    regen('mailing')


@receiver(m2m_changed, sender=User.groups.through)
def user_group_relation_changed(**kwargs):
    action = kwargs['action']
    if action in ('post_add', 'post_remove', 'post_clear'):
        user = kwargs['instance']
        user.ldap_sync(base=False,
                       access_refresh=False,
                       mac_refresh=False,
                       group_refresh=True)


@receiver(post_delete, sender=Adherent)
@receiver(post_delete, sender=Club)
@receiver(post_delete, sender=User)
def user_post_delete(**kwargs):
    """Post delete d'un user, on supprime son instance ldap"""
    user = kwargs['instance']
    user.ldap_del()
    regen('mailing')


class ServiceUser(RevMixin, AclMixin, AbstractBaseUser):
    """ Classe des users daemons, règle leurs accès au ldap"""
    readonly = 'readonly'
    ACCESS = (
        ('auth', 'auth'),
        ('readonly', 'readonly'),
        ('usermgmt', 'usermgmt'),
    )

    username = models.CharField(
        max_length=32,
        unique=True,
        help_text=_("Must only contain letters, numerals or dashes."),
        validators=[linux_user_validator]
    )
    access_group = models.CharField(
        choices=ACCESS,
        default=readonly,
        max_length=32
    )
    comment = models.CharField(
        help_text=_("Comment"),
        max_length=255,
        blank=True
    )

    USERNAME_FIELD = 'username'
    objects = UserManager()

    class Meta:
        verbose_name = _("service user")
        verbose_name_plural = _("service users")

    def get_full_name(self):
        """ Renvoie le nom complet du serviceUser formaté nom/prénom"""
        return _("Service user <{name}>").format(name=self.username)

    def get_short_name(self):
        """ Renvoie seulement le nom"""
        return self.username

    def ldap_sync(self):
        """ Synchronisation du ServiceUser dans sa version ldap"""
        try:
            user_ldap = LdapServiceUser.objects.get(name=self.username)
        except LdapServiceUser.DoesNotExist:
            user_ldap = LdapServiceUser(name=self.username)
        user_ldap.user_password = self.password[:6] + self.password[7:]
        user_ldap.save()
        self.serviceuser_group_sync()

    def ldap_del(self):
        """Suppression de l'instance ldap d'un service user"""
        try:
            user_ldap = LdapServiceUser.objects.get(name=self.username)
            user_ldap.delete()
        except LdapUser.DoesNotExist:
            pass
        self.serviceuser_group_sync()

    def serviceuser_group_sync(self):
        """Synchronise le groupe et les droits de groupe dans le ldap"""
        try:
            group = LdapServiceUserGroup.objects.get(name=self.access_group)
        except:
            group = LdapServiceUserGroup(name=self.access_group)
        group.members = list(LdapServiceUser.objects.filter(
            name__in=[user.username for user in ServiceUser.objects.filter(
                access_group=self.access_group
            )]).values_list('dn', flat=True))
        group.save()

    def __str__(self):
        return self.username


@receiver(post_save, sender=ServiceUser)
def service_user_post_save(**kwargs):
    """ Synchronise un service user ldap après modification django"""
    service_user = kwargs['instance']
    service_user.ldap_sync()


@receiver(post_delete, sender=ServiceUser)
def service_user_post_delete(**kwargs):
    """ Supprime un service user ldap après suppression django"""
    service_user = kwargs['instance']
    service_user.ldap_del()


class School(RevMixin, AclMixin, models.Model):
    """A institute in which students study"""
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
    )

    class Meta:
        verbose_name = _("school")
        verbose_name_plural = _("schools")

    def __str__(self):
        return self.name


class ListRight(RevMixin, AclMixin, Group):
    """ Ensemble des droits existants. Chaque droit crée un groupe
    ldap synchronisé, avec gid.
    Permet de gérer facilement les accès serveurs et autres
    La clef de recherche est le gid, pour cette raison là
    il n'est plus modifiable après creation"""

    unix_name = models.CharField(
        max_length=255,
        unique=True,
        validators=[RegexValidator(
            '^[a-z]+$',
            message=(_("UNIX groups can only contain lower case letters."))
        )]
    )
    gid = models.PositiveIntegerField(unique=True, null=True)
    critical = models.BooleanField(default=False)
    details = models.CharField(
        help_text=_("Description"),
        max_length=255,
        blank=True
    )

    class Meta:
        verbose_name = _("group of rights")
        verbose_name_plural = _("groups of rights")

    def __str__(self):
        return self.name

    def ldap_sync(self):
        """Sychronise les groups ldap avec le model listright coté django"""
        try:
            group_ldap = LdapUserGroup.objects.get(gid=self.gid)
        except LdapUserGroup.DoesNotExist:
            group_ldap = LdapUserGroup(gid=self.gid)
        group_ldap.name = self.unix_name
        group_ldap.members = [user.username for user
                              in self.user_set.all()]
        group_ldap.save()

    def ldap_del(self):
        """Supprime un groupe ldap"""
        try:
            group_ldap = LdapUserGroup.objects.get(gid=self.gid)
            group_ldap.delete()
        except LdapUserGroup.DoesNotExist:
            pass


@receiver(post_save, sender=ListRight)
def listright_post_save(**kwargs):
    """ Synchronise le droit ldap quand il est modifié"""
    right = kwargs['instance']
    right.ldap_sync()


@receiver(post_delete, sender=ListRight)
def listright_post_delete(**kwargs):
    """Suppression d'un groupe ldap après suppression coté django"""
    right = kwargs['instance']
    right.ldap_del()


class ListShell(RevMixin, AclMixin, models.Model):
    """A linux shell that members can use"""
    shell = models.CharField(
        verbose_name=_('path'),
        max_length=255,
        unique=True,
    )

    class Meta:
        verbose_name = _("shell")
        verbose_name_plural = _("shells")

    def get_pretty_name(self):
        """Return the canonical name of the shell"""
        return self.shell.split("/")[-1]

    def __str__(self):
        return self.shell


class Ban(RevMixin, AclMixin, models.Model):
    """A ban"""

    STATE_HARD = 0
    STATE_SOFT = 1
    STATE_BRIDAGE = 2
    STATES = (
        (0, _("HARD (no access)")),
        (1, _("SOFT (local access only)")),
        (2, _("RESTRICTED (speed limitation)")),
    )

    user = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        verbose_name=_('user'),
    )
    raison = models.CharField(
        verbose_name=_('cause'),
        max_length=255,
    )
    date_start = models.DateTimeField(
        verbose_name=_('start date'),
        auto_now_add=True,
    )
    date_end = models.DateTimeField(
        verbose_name=_('end date'),
    )
    state = models.IntegerField(
        verbose_name=_('state'),
        choices=STATES,
        default=STATE_HARD,
    )

    class Meta:
        verbose_name = _("ban")
        verbose_name_plural = _("bans")

    def notif_ban(self):
        """ Prend en argument un objet ban, envoie un mail de notification """
        template = loader.get_template('users/email_ban_notif')
        context = {
            'name': self.user.get_full_name(),
            'raison': self.raison,
            'date_end': self.date_end,
            'asso_name': AssoOption.get_cached_value('name'),
        }
        send_mail(
            'Déconnexion disciplinaire / Disciplinary disconnection',
            template.render(context),
            GeneralOption.get_cached_value('email_from'),
            [self.user.email],
            fail_silently=False
        )
        return

    def is_active(self):
        """Ce ban est-il actif?"""
        return self.date_end > timezone.now()

    def can_view(self, user_request, *_args, **_kwargs):
        """Check if an user can view a Ban object.

        :param self: The targeted object.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
        text
        """
        if (not user_request.has_perm('users.view_ban') and
                self.user != user_request):
            return False, (_("You don't have the right to view bans other"
                             " than yours."))
        else:
            return True, None

    def __str__(self):
        return str(self.user) + ' ' + str(self.raison)


@receiver(post_save, sender=Ban)
def ban_post_save(**kwargs):
    """ Regeneration de tous les services après modification d'un ban"""
    ban = kwargs['instance']
    is_created = kwargs['created']
    user = ban.user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    regen('mailing')
    if is_created:
        ban.notif_ban()
        regen('dhcp')
        regen('mac_ip_list')
    if user.has_access():
        regen('dhcp')
        regen('mac_ip_list')


@receiver(post_delete, sender=Ban)
def ban_post_delete(**kwargs):
    """ Regen de tous les services après suppression d'un ban"""
    user = kwargs['instance'].user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    regen('mailing')
    regen('dhcp')
    regen('mac_ip_list')


class Whitelist(RevMixin, AclMixin, models.Model):
    """A whitelist item

    The member doesn't pay but get internet access.
    Less powerful than a ban.
    """
    user = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        verbose_name=_('user'),
    )
    raison = models.CharField(
        verbose_name=_('cause'),
        max_length=255,
    )
    date_start = models.DateTimeField(
        verbose_name=_('start date'),
        auto_now_add=True,
    )
    date_end = models.DateTimeField(
        verbose_name=_('end date'),
    )

    class Meta:
        verbose_name = _("whitelist (free of charge access)")
        verbose_name_plural = _("whitelists (free of charge access)")

    def is_active(self):
        """ Is this whitelisting active ? """
        return self.date_end > timezone.now()

    def can_view(self, user_request, *_args, **_kwargs):
        """Check if an user can view a Whitelist object.

        :param self: The targeted object.
        :param user_request: The user who ask for viewing the target.
        :return: A boolean telling if the acces is granted and an explanation
        text
        """
        if (not user_request.has_perm('users.view_whitelist') and
                self.user != user_request):
            return False, (_("You don't have the right to view whitelists"
                             " other than yours."))
        else:
            return True, None

    def __str__(self):
        return str(self.user) + ' ' + str(self.raison)


@receiver(post_save, sender=Whitelist)
def whitelist_post_save(**kwargs):
    """Après modification d'une whitelist, on synchronise les services
    et on lui permet d'avoir internet"""
    whitelist = kwargs['instance']
    user = whitelist.user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    is_created = kwargs['created']
    regen('mailing')
    if is_created:
        regen('dhcp')
        regen('mac_ip_list')
    if user.has_access():
        regen('dhcp')
        regen('mac_ip_list')


@receiver(post_delete, sender=Whitelist)
def whitelist_post_delete(**kwargs):
    """Après suppression d'une whitelist, on supprime l'accès internet
    en forçant la régénration"""
    user = kwargs['instance'].user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)
    regen('mailing')
    regen('dhcp')
    regen('mac_ip_list')


class LdapUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """
    # LDAP meta-data
    base_dn = LDAP['base_user_dn']
    object_classes = ['inetOrgPerson', 'top', 'posixAccount',
                      'sambaSamAccount', 'radiusprofile',
                      'shadowAccount']

    # attributes
    gid = ldapdb.models.fields.IntegerField(db_column='gidNumber')
    name = ldapdb.models.fields.CharField(
        db_column='cn',
        max_length=200
    )
    uid = ldapdb.models.fields.CharField(db_column='uid', max_length=200)
    uidNumber = ldapdb.models.fields.IntegerField(
        db_column='uidNumber',
        unique=True
    )
    sn = ldapdb.models.fields.CharField(db_column='sn', max_length=200)
    login_shell = ldapdb.models.fields.CharField(
        db_column='loginShell',
        max_length=200,
        blank=True,
        null=True
    )
    mail = ldapdb.models.fields.CharField(db_column='mail', max_length=200)
    given_name = ldapdb.models.fields.CharField(
        db_column='givenName',
        max_length=200
    )
    home_directory = ldapdb.models.fields.CharField(
        db_column='homeDirectory',
        max_length=200
    )
    display_name = ldapdb.models.fields.CharField(
        db_column='displayName',
        max_length=200,
        blank=True,
        null=True
    )
    dialupAccess = ldapdb.models.fields.CharField(db_column='dialupAccess')
    sambaSID = ldapdb.models.fields.IntegerField(
        db_column='sambaSID',
        unique=True
    )
    user_password = ldapdb.models.fields.CharField(
        db_column='userPassword',
        max_length=200,
        blank=True,
        null=True
    )
    sambat_nt_password = ldapdb.models.fields.CharField(
        db_column='sambaNTPassword',
        max_length=200,
        blank=True,
        null=True
    )
    macs = ldapdb.models.fields.ListField(
        db_column='radiusCallingStationId',
        max_length=200,
        blank=True,
        null=True
    )
    shadowexpire = ldapdb.models.fields.CharField(
        db_column='shadowExpire',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.sn = self.name
        self.uid = self.name
        self.sambaSID = self.uidNumber
        super(LdapUser, self).save(*args, **kwargs)


class LdapUserGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP group entry.

    Un groupe ldap
    """
    # LDAP meta-data
    base_dn = LDAP['base_usergroup_dn']
    object_classes = ['posixGroup']

    # attributes
    gid = ldapdb.models.fields.IntegerField(db_column='gidNumber')
    members = ldapdb.models.fields.ListField(
        db_column='memberUid',
        blank=True
    )
    name = ldapdb.models.fields.CharField(
        db_column='cn',
        max_length=200,
    )

    def __str__(self):
        return self.name


class LdapServiceUser(ldapdb.models.Model):
    """
    Class for representing an LDAP userservice entry.

    Un user de service coté ldap
    """
    # LDAP meta-data
    base_dn = LDAP['base_userservice_dn']
    object_classes = ['applicationProcess', 'simpleSecurityObject']

    # attributes
    name = ldapdb.models.fields.CharField(
        db_column='cn',
        max_length=200
    )
    user_password = ldapdb.models.fields.CharField(
        db_column='userPassword',
        max_length=200,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class LdapServiceUserGroup(ldapdb.models.Model):
    """
    Class for representing an LDAP userservice entry.

    Un group user de service coté ldap. Dans userservicegroupdn
    (voir dans settings_local.py)
    """
    # LDAP meta-data
    base_dn = LDAP['base_userservicegroup_dn']
    object_classes = ['groupOfNames']

    # attributes
    name = ldapdb.models.fields.CharField(
        db_column='cn',
        max_length=200
    )
    members = ldapdb.models.fields.ListField(
        db_column='member',
        blank=True
    )

    def __str__(self):
        return self.name


class EMailAddress(RevMixin, AclMixin, models.Model):
    """Defines a local email account for a user
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text=_("User of the local email account")
    )
    local_part = models.CharField(
        unique=True,
        max_length=128,
        help_text=_("Local part of the email address")
    )

    class Meta:
        verbose_name = _("local email account")
        verbose_name_plural = _("local email accounts")

    def __str__(self):
        return str(self.local_part) + OptionalUser.get_cached_value('local_email_domain')

    @cached_property
    def complete_email_address(self):
        return str(self.local_part) + OptionalUser.get_cached_value('local_email_domain')

    @staticmethod
    def can_create(user_request, userid, *_args, **_kwargs):
        """Check if a user can create a `EMailAddress` object.

        Args:
            user_request: The user who wants to create the object.
            userid: The id of the user to whom the account is to be created

        Returns:
            a message and a boolean which is True if the user can create
            a local email account.
        """
        if user_request.has_perm('users.add_emailaddress'):
            return True, None
        if not OptionalUser.get_cached_value('local_email_accounts_enabled'):
            return False, _("The local email accounts are not enabled.")
        if int(user_request.id) != int(userid):
            return False, _("You don't have the right to add a local email"
                            " account to another user.")
        elif user_request.email_address.count() >= OptionalUser.get_cached_value('max_email_address'):
            return False, _("You reached the limit of {} local email accounts.").format(
                OptionalUser.get_cached_value('max_email_address')
            )
        return True, None

    def can_view(self, user_request, *_args, **_kwargs):
        """Check if a user can view the local email account

        Args:
            user_request: The user who wants to view the object.

        Returns:
            a message and a boolean which is True if the user can see
            the local email account.
        """
        if user_request.has_perm('users.view_emailaddress'):
            return True, None
        if not OptionalUser.get_cached_value('local_email_accounts_enabled'):
            return False, _("The local email accounts are not enabled.")
        if user_request == self.user:
            return True, None
        return False, _("You don't have the right to edit another user's local"
                        " email account.")

    def can_delete(self, user_request, *_args, **_kwargs):
        """Check if a user can delete the alias

        Args:
            user_request: The user who wants to delete the object.

        Returns:
            a message and a boolean which is True if the user can delete
            the local email account.
        """
        if self.local_part == self.user.username.lower():
            return False, _("You can't delete a local email account whose"
                            " local part is the same as the username.")
        if user_request.has_perm('users.delete_emailaddress'):
            return True, None
        if not OptionalUser.get_cached_value('local_email_accounts_enabled'):
            return False, _("The local email accounts are not enabled.")
        if user_request == self.user:
            return True, None
        return False, _("You don't have the right to delete another user's"
                       " local email account")

    def can_edit(self, user_request, *_args, **_kwargs):
        """Check if a user can edit the alias

        Args:
            user_request: The user who wants to edit the object.

        Returns:
            a message and a boolean which is True if the user can edit
            the local email account.
        """
        if self.local_part == self.user.username.lower():
            return False, _("You can't edit a local email account whose local"
                            " part is the same as the username.")
        if user_request.has_perm('users.change_emailaddress'):
            return True, None
        if not OptionalUser.get_cached_value('local_email_accounts_enabled'):
            return False, _("The local email accounts are not enabled.")
        if user_request == self.user:
            return True, None
        return False, _("You don't have the right to edit another user's local"
                        " email account.")

    def clean(self, *args, **kwargs):
        self.local_part = self.local_part.lower()
        if "@" in self.local_part or "+" in self.local_part:
            raise ValidationError(_("The local part must not contain @ or +."))
        result, reason = smtp_check(self.local_part)
        if result:
            raise ValidationError(reason)
        super(EMailAddress, self).clean(*args, **kwargs)
