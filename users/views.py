# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2017  Lemesle Augustin

"""
Module des views.

On définit les vues pour l'ajout, l'edition des users : infos personnelles,
mot de passe, etc

Permet aussi l'ajout, edition et suppression des droits, des bannissements,
des whitelist, des services users et des écoles
"""

from __future__ import unicode_literals

from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import ProtectedError, Count, Max
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from rest_framework.renderers import JSONRenderer
from reversion import revisions as reversion

from cotisations.models import Facture, Paiement
from machines.models import Machine
from preferences.models import OptionalUser, GeneralOption, AssoOption
from re2o.views import form
from re2o.utils import (
    all_has_access,
)
from re2o.base import (
    re2o_paginator,
    SortTable
)
from re2o.acl import (
    can_create,
    can_edit,
    can_delete_set,
    can_delete,
    can_view,
    can_view_all,
    can_change
)
from cotisations.utils import find_payment_method
from topologie.models import Port
from .serializers import MailingSerializer, MailingMemberSerializer
from .models import (
    User,
    Ban,
    Whitelist,
    School,
    ListRight,
    Request,
    ServiceUser,
    Adherent,
    Club,
    ListShell,
    EMailAddress,
)
from .forms import (
    BanForm,
    WhitelistForm,
    EMailAddressForm,
    EmailSettingsForm,
    DelSchoolForm,
    DelListRightForm,
    NewListRightForm,
    StateForm,
    SchoolForm,
    ShellForm,
    EditServiceUserForm,
    ServiceUserForm,
    ListRightForm,
    AdherentCreationForm,
    AdherentEditForm,
    ClubForm,
    MassArchiveForm,
    PassForm,
    ResetPasswordForm,
    ClubAdminandMembersForm,
    GroupForm,
    InitialRegisterForm
)


@can_create(Adherent)
def new_user(request):
    """ Vue de création d'un nouvel utilisateur,
    envoie un mail pour le mot de passe"""
    user = AdherentCreationForm(request.POST or None, user=request.user)
    GTU_sum_up = GeneralOption.get_cached_value('GTU_sum_up')
    GTU = GeneralOption.get_cached_value('GTU')
    if user.is_valid():
        user = user.save()
        user.reset_passwd_mail(request)
        messages.success(request, _("The user %s was created, an email to set"
                                    " the password was sent.") % user.pseudo)
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(user.id)}
        ))
    return form(
        {
            'userform': user,
            'GTU_sum_up': GTU_sum_up,
            'GTU': GTU,
            'showCGU': True,
            'action_name': _("Commit")
        },
        'users/user.html',
        request
    )


@login_required
@can_create(Club)
def new_club(request):
    """ Vue de création d'un nouveau club,
    envoie un mail pour le mot de passe"""
    club = ClubForm(request.POST or None, user=request.user)
    if club.is_valid():
        club = club.save(commit=False)
        club.save()
        club.reset_passwd_mail(request)
        messages.success(request, _("The club %s was created, an email to set"
                                    " the password was sent.") % club.pseudo)
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(club.id)}
        ))
    return form(
        {'userform': club, 'showCGU': False, 'action_name': _("Create a club")},
        'users/user.html',
        request
    )


@login_required
@can_edit(Club)
def edit_club_admin_members(request, club_instance, **_kwargs):
    """Vue d'edition de la liste des users administrateurs et
    membres d'un club"""
    club = ClubAdminandMembersForm(
        request.POST or None,
        instance=club_instance
    )
    if club.is_valid():
        if club.changed_data:
            club.save()
            messages.success(request, _("The club was edited."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(club_instance.id)}
        ))
    return form(
        {
            'userform': club,
            'showCGU': False,
            'action_name': _("Edit the admins and members")
        },
        'users/user.html',
        request
    )


@login_required
@can_edit(User)
def edit_info(request, user, userid):
    """ Edite un utilisateur à partir de son id,
    si l'id est différent de request.user, vérifie la
    possession du droit cableur """
    if user.is_class_adherent:
        user_form = AdherentEditForm(
            request.POST or None,
            instance=user.adherent,
            user=request.user
        )
    else:
        user_form = ClubForm(
            request.POST or None,
            instance=user.club,
            user=request.user
        )
    if user_form.is_valid():
        if user_form.changed_data:
            user_form.save()
            messages.success(request, _("The user was edited."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(userid)}
        ))
    return form(
        {'userform': user_form, 'action_name': _("Edit the user")},
        'users/user.html',
        request
    )


@login_required
@can_edit(User, 'state')
def state(request, user, userid):
    """ Change the state (active/unactive/archived) of a user"""
    state_form = StateForm(request.POST or None, instance=user)
    if state_form.is_valid():
        if state_form.changed_data:
            state_form.save()
            messages.success(request, _("The state was edited."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(userid)}
        ))
    return form(
        {'userform': state_form, 'action_name': _("Edit the state")},
        'users/user.html',
        request
    )


@login_required
@can_edit(User, 'groups')
def groups(request, user, userid):
    """ View to edit the groups of a user """
    group_form = GroupForm(request.POST or None,
                           instance=user, user=request.user)
    if group_form.is_valid():
        if group_form.changed_data:
            group_form.save()
            messages.success(request, _("The groups were edited."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(userid)}
        ))
    return form(
        {'userform': group_form, 'action_name': _("Edit the groups")},
        'users/user.html',
        request
    )


@login_required
@can_edit(User, 'password')
def password(request, user, userid):
    """ Reinitialisation d'un mot de passe à partir de l'userid,
    pour self par défaut, pour tous sans droit si droit cableur,
    pour tous si droit bureau """
    u_form = PassForm(request.POST or None, instance=user, user=request.user)
    if u_form.is_valid():
        if u_form.changed_data:
            u_form.save()
            messages.success(request, _("The password was changed."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(userid)}
        ))
    return form(
        {'userform': u_form, 'action_name': _("Change the password")},
        'users/user.html',
        request
    )


@login_required
@can_edit(User, 'groups')
def del_group(request, user, listrightid, **_kwargs):
    """ View used to delete a group """
    user.groups.remove(ListRight.objects.get(id=listrightid))
    user.save()
    messages.success(request, _("%s was removed from the group.") % user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@can_edit(User, 'is_superuser')
def del_superuser(request, user, **_kwargs):
    """Remove the superuser right of an user."""
    user.is_superuser = False
    user.save()
    messages.success(request, _("%s is no longer superuser.") % user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@can_create(ServiceUser)
def new_serviceuser(request):
    """ Vue de création d'un nouvel utilisateur service"""
    user = ServiceUserForm(request.POST or None)
    if user.is_valid():
        user.save()
        messages.success(
            request,
            _("The service user was created.")
        )
        return redirect(reverse('users:index-serviceusers'))
    return form(
        {'userform': user, 'action_name': _("Create a service user")},
        'users/user.html',
        request
    )


@login_required
@can_edit(ServiceUser)
def edit_serviceuser(request, serviceuser, **_kwargs):
    """ Edit a ServiceUser """
    serviceuser = EditServiceUserForm(
        request.POST or None,
        instance=serviceuser
    )
    if serviceuser.is_valid():
        if serviceuser.changed_data:
            serviceuser.save()
        messages.success(request, _("The service user was edited."))
        return redirect(reverse('users:index-serviceusers'))
    return form(
        {'userform': serviceuser, 'action_name': _("Edit a service user")},
        'users/user.html',
        request
    )


@login_required
@can_delete(ServiceUser)
def del_serviceuser(request, serviceuser, **_kwargs):
    """Suppression d'un ou plusieurs serviceusers"""
    if request.method == "POST":
        serviceuser.delete()
        messages.success(request, _("The service user was deleted."))
        return redirect(reverse('users:index-serviceusers'))
    return form(
        {'objet': serviceuser, 'objet_name': 'service user'},
        'users/delete.html',
        request
    )


@login_required
@can_create(EMailAddress)
@can_edit(User)
def add_emailaddress(request, user, userid):
    """ Create a new local email account"""
    emailaddress_instance = EMailAddress(user=user)
    emailaddress = EMailAddressForm(
        request.POST or None,
        instance=emailaddress_instance
    )
    if emailaddress.is_valid():
        emailaddress.save()
        messages.success(request, _("The local email account was created."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(userid)}
        ))
    return form(
        {'userform': emailaddress,
         'showCGU': False,
         'action_name': _("Add a local email account")},
        'users/user.html',
        request
    )


@login_required
@can_edit(EMailAddress)
def edit_emailaddress(request, emailaddress_instance, **_kwargs):
    """ Edit a local email account"""
    emailaddress = EMailAddressForm(
        request.POST or None,
        instance=emailaddress_instance
    )
    if emailaddress.is_valid():
        if emailaddress.changed_data:
            emailaddress.save()
            messages.success(request, _("The local email account was edited."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(emailaddress_instance.user.id)}
        ))
    return form(
        {'userform': emailaddress,
         'showCGU': False,
         'action_name': _("Edit a local email account")},
        'users/user.html',
        request
    )


@login_required
@can_delete(EMailAddress)
def del_emailaddress(request, emailaddress, **_kwargs):
    """Delete a local email account"""
    if request.method == "POST":
        emailaddress.delete()
        messages.success(request, _("The local email account was deleted."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(emailaddress.user.id)}
            ))
    return form(
        {'objet': emailaddress, 'objet_name': 'emailaddress'},
        'users/delete.html',
        request
    )


@login_required
@can_edit(User)
def edit_email_settings(request, user_instance, **_kwargs):
    """Edit the email settings of a user"""
    email_settings = EmailSettingsForm(
        request.POST or None,
        instance=user_instance,
        user=request.user
    )
    if email_settings.is_valid():
        if email_settings.changed_data:
            email_settings.save()
            messages.success(request, _("The email settings were edited."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(user_instance.id)}
            ))
    return form(
        {'userform': email_settings,
         'showCGU': False,
         'load_js_file': '/static/js/email_address.js',
         'action_name': _("Edit the email settings")},
        'users/user.html',
        request
    )


@login_required
@can_create(ListRight)
def add_listright(request):
    """ Ajouter un droit/groupe, nécessite droit bureau.
    Obligation de fournir un gid pour la synchro ldap, unique """
    listright = NewListRightForm(request.POST or None)
    if listright.is_valid():
        listright.save()
        messages.success(request, _("The group of rights was added."))
        return redirect(reverse('users:index-listright'))
    return form(
        {'userform': listright, 'action_name': _("Add a group of rights")},
        'users/user.html',
        request
    )


@login_required
@can_edit(ListRight)
def edit_listright(request, listright_instance, **_kwargs):
    """ Editer un groupe/droit, necessite droit bureau,
    à partir du listright id """
    listright = ListRightForm(
        request.POST or None,
        instance=listright_instance
    )
    if listright.is_valid():
        if listright.changed_data:
            listright.save()
            messages.success(request, _("The group of rights was edited."))
        return redirect(reverse('users:index-listright'))
    return form(
        {'userform': listright, 'action_name': _("Edit a group of rights")},
        'users/user.html',
        request
    )


@login_required
@can_delete_set(ListRight)
def del_listright(request, instances):
    """ Supprimer un ou plusieurs groupe, possible si il est vide, need droit
    bureau """
    listright = DelListRightForm(request.POST or None, instances=instances)
    if listright.is_valid():
        listright_dels = listright.cleaned_data['listrights']
        for listright_del in listright_dels:
            try:
                listright_del.delete()
                messages.success(request, _("The group of rights was"
                                            " deleted."))
            except ProtectedError:
                messages.error(
                    request,
                    _("The group of rights %s is assigned to at least one"
                      " user, impossible to delete it.") % listright_del)
        return redirect(reverse('users:index-listright'))
    return form(
        {'userform': listright, 'action_name': _("Delete")},
        'users/user.html',
        request
    )


@login_required
@can_view_all(User)
@can_change(User, 'state')
def mass_archive(request):
    """ Permet l'archivage massif"""
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    to_archive_form = MassArchiveForm(request.POST or None)
    to_archive_list = []
    if to_archive_form.is_valid():
        date = to_archive_form.cleaned_data['date']
        full_archive = to_archive_form.cleaned_data['full_archive']
        to_archive_list = User.objects.exclude(id__in=all_has_access()).exclude(id__in=all_has_access(search_time=date)).exclude(state=User.STATE_NOT_YET_ACTIVE).exclude(state=User.STATE_FULL_ARCHIVE)
        if not full_archive:
            to_archive_list = to_archive_list.exclude(state=User.STATE_ARCHIVE)
        if "valider" in request.POST:
            if full_archive:
                User.mass_full_archive(to_archive_list)
            else:
                User.mass_archive(to_archive_list)
            messages.success(request, _("%s users were archived.") %
                to_archive_list.count()
            )
            return redirect(reverse('users:index'))
        to_archive_list = re2o_paginator(request, to_archive_list, pagination_number)
    return form(
        {'userform': to_archive_form, 'to_archive_list': to_archive_list},
        'users/mass_archive.html',
        request
    )


@login_required
@can_view_all(Adherent)
def index(request):
    """ Affiche l'ensemble des adherents, need droit cableur """
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    users_list = Adherent.objects.select_related('room')
    users_list = SortTable.sort(
        users_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.USERS_INDEX
    )
    users_list = re2o_paginator(request, users_list, pagination_number)
    return render(request, 'users/index.html', {'users_list': users_list})


@login_required
@can_view_all(Club)
def index_clubs(request):
    """ Affiche l'ensemble des clubs, need droit cableur """
    pagination_number = GeneralOption.get_cached_value('pagination_number')
    clubs_list = Club.objects.select_related('room')
    clubs_list = SortTable.sort(
        clubs_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.USERS_INDEX
    )
    clubs_list = re2o_paginator(request, clubs_list, pagination_number)
    return render(
        request,
        'users/index_clubs.html',
        {'clubs_list': clubs_list}
    )


@login_required
@can_view_all(ListRight)
def index_listright(request):
    """ Affiche l'ensemble des droits"""
    rights = {}
    for right in (ListRight.objects
                  .order_by('name')
                  .prefetch_related('permissions')
                  .prefetch_related('user_set')
                  .prefetch_related('user_set__facture_set__vente_set__cotisation')
                 ):
        rights[right] = (right.user_set
                         .annotate(action_number=Count('revision'),
                                   last_seen=Max('revision__date_created'),
                                   end_adhesion=Max('facture__vente__cotisation__date_end'))
                        )
    superusers = (User.objects
                  .filter(is_superuser=True)
                  .annotate(action_number=Count('revision'),
                            last_seen=Max('revision__date_created'),
                            end_adhesion=Max('facture__vente__cotisation__date_end'))
                 )
    return render(
        request,
        'users/index_listright.html',
        {
            'rights': rights,
            'superusers' : superusers,
        }
    )


@login_required
@can_view_all(ServiceUser)
def index_serviceusers(request):
    """ Affiche les users de services (pour les accès ldap)"""
    serviceusers_list = ServiceUser.objects.order_by('pseudo')
    return render(
        request,
        'users/index_serviceusers.html',
        {'serviceusers_list': serviceusers_list}
    )


@login_required
def mon_profil(request):
    """ Lien vers profil, renvoie request.id à la fonction """
    return redirect(reverse(
        'users:profil',
        kwargs={'userid': str(request.user.id)}
    ))


@login_required
@can_view(User)
def profil(request, users, **_kwargs):
    """ Affiche un profil, self or cableur, prend un userid en argument """
    machines = Machine.objects.filter(user=users).select_related('user')\
        .prefetch_related('interface_set__domain__extension')\
        .prefetch_related('interface_set__ipv4__ip_type__extension')\
        .prefetch_related('interface_set__machine_type')\
        .prefetch_related('interface_set__domain__related_domain__extension')
    machines = SortTable.sort(
        machines,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.MACHINES_INDEX
    )
    pagination_large_number = GeneralOption.get_cached_value(
        'pagination_large_number'
    )
    nb_machines = machines.count()
    machines = re2o_paginator(request, machines, pagination_large_number)
    factures = Facture.objects.filter(user=users)
    factures = SortTable.sort(
        factures,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.COTISATIONS_INDEX
    )
    bans = Ban.objects.filter(user=users)
    bans = SortTable.sort(
        bans,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.USERS_INDEX_BAN
    )
    whitelists = Whitelist.objects.filter(user=users)
    whitelists = SortTable.sort(
        whitelists,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.USERS_INDEX_WHITE
    )
    try:
        balance = find_payment_method(Paiement.objects.get(is_balance=True))
    except Paiement.DoesNotExist:
        user_solde = False
    else:
        user_solde = (
            balance is not None
            and balance.can_credit_balance(request.user)
        )
    return render(
        request,
        'users/profil.html',
        {
            'users': users,
            'machines_list': machines,
            'nb_machines': nb_machines,
            'facture_list': factures,
            'ban_list': bans,
            'white_list': whitelists,
            'user_solde': user_solde,
            'solde_activated': Paiement.objects.filter(is_balance=True).exists(),
            'asso_name': AssoOption.objects.first().name,
            'emailaddress_list': users.email_address,
            'local_email_accounts_enabled': (
                OptionalUser.objects.first().local_email_accounts_enabled
            )
        }
    )


def reset_password(request):
    """ Reintialisation du mot de passe si mdp oublié """
    userform = ResetPasswordForm(request.POST or None)
    if userform.is_valid():
        try:
            user = User.objects.get(
                pseudo=userform.cleaned_data['pseudo'],
                email=userform.cleaned_data['email'],
                state__in=[User.STATE_ACTIVE, User.STATE_NOT_YET_ACTIVE],
            )
        except User.DoesNotExist:
            messages.error(request, _("The user doesn't exist."))
            return form(
                {'userform': userform, 'action_name': _("Reset")},
                'users/user.html',
                request
            )
        user.reset_passwd_mail(request)
        messages.success(request, _("An email to reset the password was sent."))
        redirect(reverse('index'))
    return form(
        {'userform': userform, 'action_name': _("Reset")},
        'users/user.html',
        request
    )


def process(request, token):
    """Process, lien pour la reinitialisation du mot de passe"""
    valid_reqs = Request.objects.filter(expires_at__gt=timezone.now())
    req = get_object_or_404(valid_reqs, token=token)

    if req.type == Request.PASSWD:
        return process_passwd(request, req)
    else:
        messages.error(request, _("Error: please contact an admin."))
        redirect(reverse('index'))


def process_passwd(request, req):
    """Process le changeemnt de mot de passe, renvoie le formulaire
    demandant le nouveau password"""
    user = req.user
    u_form = PassForm(request.POST or None, instance=user, user=request.user)
    if u_form.is_valid():
        with transaction.atomic(), reversion.create_revision():
            u_form.save()
            reversion.set_comment(_("Password reset"))
        req.delete()
        messages.success(request, _("The password was changed."))
        return redirect(reverse('index'))
    return form(
        {'userform': u_form, 'action_name': _("Change the password")},
        'users/user.html',
        request
    )

@login_required
def initial_register(request):
    switch_ip = request.GET.get('switch_ip', None)
    switch_port = request.GET.get('switch_port', None)
    client_mac = request.GET.get('client_mac', None)
    u_form = InitialRegisterForm(request.POST or None, user=request.user, switch_ip=switch_ip, switch_port=switch_port, client_mac=client_mac)
    if not u_form.fields:
        messages.error(request, _("Incorrect URL, or already registered device."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(request.user.id)}
        ))
    if switch_ip and switch_port:
        port = Port.objects.filter(switch__interface__ipv4__ipv4=switch_ip, port=switch_port).first()
    if u_form.is_valid():
        messages.success(request, _("Successful registration! Please"
                                    " disconnect and reconnect your Ethernet"
                                    " cable to get Internet access."))
        return form(
            {},
            'users/plugin_out.html',
            request
        )
    return form(
        {'userform': u_form, 'port': port, 'mac': client_mac},
        'users/user_autocapture.html',
        request
    )


class JSONResponse(HttpResponse):
    """ Framework Rest """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def ml_std_list(_request):
    """ API view sending all the available standard mailings"""
    return JSONResponse([
        {'name': 'adherents'}
    ])


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def ml_std_members(request, ml_name):
    """ API view sending all the members for a standard mailing"""
    # All with active connextion
    if ml_name == 'adherents':
        members = all_has_access().values('email').distinct()
    # Unknown mailing
    else:
        messages.error(request, _("The mailing list doesn't exist."))
        return redirect(reverse('index'))
    seria = MailingMemberSerializer(members, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def ml_club_list(_request):
    """ API view sending all the available club mailings"""
    clubs = Club.objects.filter(mailing=True).values('pseudo')
    seria = MailingSerializer(clubs, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def ml_club_admins(request, ml_name):
    """ API view sending all the administrators for a specific club mailing"""
    try:
        club = Club.objects.get(mailing=True, pseudo=ml_name)
    except Club.DoesNotExist:
        messages.error(request, _("The mailing list doesn't exist."))
        return redirect(reverse('index'))
    members = club.administrators.all().values('email').distinct()
    seria = MailingMemberSerializer(members, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def ml_club_members(request, ml_name):
    """ API view sending all the members for a specific club mailing"""
    try:
        club = Club.objects.get(mailing=True, pseudo=ml_name)
    except Club.DoesNotExist:
        messages.error(request, _("The mailing list doesn't exist."))
        return redirect(reverse('index'))
    members = (
        club.administrators.all().values('email').distinct() |
        club.members.all().values('email').distinct()
    )
    seria = MailingMemberSerializer(members, many=True)
    return JSONResponse(seria.data)

