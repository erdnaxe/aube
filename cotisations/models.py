# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2018  Hugo Levy-Falk

"""
The database models for the 'cotisation' app of re2o.
The goal is to keep the main actions here, i.e. the 'clean' and 'save'
function are higly reposnsible for the changes, checking the coherence of the
data and the good behaviour in general for not breaking the database.

For further details on each of those models, see the documentation details for
each.
"""

from __future__ import unicode_literals
from dateutil.relativedelta import relativedelta

from django.db import models
from django.db.models import Q, Max
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages

from preferences.models import CotisationsOption
from machines.models import regen
from re2o.field_permissions import FieldPermissionModelMixin
from re2o.mixins import AclMixin, RevMixin

from cotisations.utils import (
    find_payment_method, send_mail_invoice, send_mail_voucher
)
from cotisations.validators import check_no_balance


class BaseInvoice(RevMixin, AclMixin, FieldPermissionModelMixin, models.Model):
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date")
    )

    # TODO : change prix to price
    def prix(self):
        """
        Returns: the raw price without the quantities.
        Deprecated, use :total_price instead.
        """
        price = Vente.objects.filter(
            facture=self
        ).aggregate(models.Sum('prix'))['prix__sum']
        return price

    # TODO : change prix to price
    def prix_total(self):
        """
        Returns: the total price for an invoice. Sum all the articles' prices
        and take the quantities into account.
        """
        # TODO : change Vente to somethingelse
        return Vente.objects.filter(
            facture=self
        ).aggregate(
            total=models.Sum(
                models.F('prix')*models.F('number'),
                output_field=models.DecimalField()
            )
        )['total'] or 0

    def name(self):
        """
        Returns : a string with the name of all the articles in the invoice.
        Used for reprensenting the invoice with a string.
        """
        name = ' - '.join(Vente.objects.filter(
            facture=self
        ).values_list('name', flat=True))
        return name


# TODO : change facture to invoice
class Facture(BaseInvoice):
    """
    The model for an invoice. It reprensents the fact that a user paid for
    something (it can be multiple article paid at once).

    An invoice is linked to :
        * one or more purchases (one for each article sold that time)
        * a user (the one who bought those articles)
        * a payment method (the one used by the user)
        * (if applicable) a bank
        * (if applicable) a cheque number.
    Every invoice is dated throught the 'date' value.
    An invoice has a 'controlled' value (default : False) which means that
    someone with high enough rights has controlled that invoice and taken it
    into account. It also has a 'valid' value (default : True) which means
    that someone with high enough rights has decided that this invoice was not
    valid (thus it's like the user never paid for his articles). It may be
    necessary in case of non-payment.
    """

    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    # TODO : change paiement to payment
    paiement = models.ForeignKey('Paiement', on_delete=models.PROTECT)
    # TODO : change banque to bank
    banque = models.ForeignKey(
        'Banque',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    # TODO : maybe change to cheque nummber because not evident
    cheque = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("cheque number")
    )
    # TODO : change name to validity for clarity
    valid = models.BooleanField(
        default=False,
        verbose_name=_("validated")
    )
    # TODO : changed name to controlled for clarity
    control = models.BooleanField(
        default=False,
        verbose_name=_("controlled")
    )

    class Meta:
        abstract = False
        permissions = (
            # TODO : change facture to invoice
            ('change_facture_control',
             _("Can edit the \"controlled\" state")),
            ('change_all_facture',
             _("Can edit all the previous invoices")),
        )
        verbose_name = _("invoice")
        verbose_name_plural = _("invoices")

    def linked_objects(self):
        """Return linked objects : machine and domain.
        Usefull in history display"""
        return self.vente_set.all()

    def can_edit(self, user_request, *args, **kwargs):
        if not user_request.has_perm('cotisations.change_facture'):
            return False, _("You don't have the right to edit an invoice.")
        elif not user_request.has_perm('cotisations.change_all_facture') and \
                not self.user.can_edit(user_request, *args, **kwargs)[0]:
            return False, _("You don't have the right to edit this user's "
                            "invoices.")
        elif not user_request.has_perm('cotisations.change_all_facture') and \
                (self.control or not self.valid):
            return False, _("You don't have the right to edit an invoice "
                            "already controlled or invalidated.")
        else:
            return True, None

    def can_delete(self, user_request, *args, **kwargs):
        if not user_request.has_perm('cotisations.delete_facture'):
            return False, _("You don't have the right to delete an invoice.")
        elif not user_request.has_perm('cotisations.change_all_facture') and \
                not self.user.can_edit(user_request, *args, **kwargs)[0]:
            return False, _("You don't have the right to delete this user's "
                            "invoices.")
        elif not user_request.has_perm('cotisations.change_all_facture') and \
                (self.control or not self.valid):
            return False, _("You don't have the right to delete an invoice "
                            "already controlled or invalidated.")
        else:
            return True, None

    def can_view(self, user_request, *_args, **_kwargs):
        if not user_request.has_perm('cotisations.view_facture'):
            if self.user != user_request:
                return False, _("You don't have the right to view someone else's "
                                "invoices history.")
            elif not self.valid:
                return False, _("The invoice has been invalidated.")
            else:
                return True, None
        else:
            return True, None

    @staticmethod
    def can_change_control(user_request, *_args, **_kwargs):
        """ Returns True if the user can change the 'controlled' status of
        this invoice """
        return (
            user_request.has_perm('cotisations.change_facture_control'),
            _("You don't have the right to edit the \"controlled\" state.")
        )

    @staticmethod
    def can_create(user_request, *_args, **_kwargs):
        """Check if a user can create an invoice.

        :param user_request: The user who wants to create an invoice.
        :return: a message and a boolean which is True if the user can create
            an invoice or if the `options.allow_self_subscription` is set.
        """
        if user_request.has_perm('cotisations.add_facture'):
            return True, None
        if len(Paiement.find_allowed_payments(user_request)) <= 0:
            return False, _("There are no payment method which you can use.")
        if len(Article.find_allowed_articles(user_request, user_request)) <= 0:
            return False, _("There are no article that you can buy.")
        return True, None

    def __init__(self, *args, **kwargs):
        super(Facture, self).__init__(*args, **kwargs)
        self.field_permissions = {
            'control': self.can_change_control,
        }
        self.__original_valid = self.valid
        self.__original_control = self.control

    def get_subscription(self):
        """Returns every subscription associated with this invoice."""
        return Cotisation.objects.filter(
            vente__in=self.vente_set.filter(
                Q(type_cotisation='All') |
                Q(type_cotisation='Adhesion')
            )
        )

    def is_subscription(self):
        """Returns True if this invoice contains at least one subscribtion."""
        return bool(self.get_subscription())

    def save(self, *args, **kwargs):
        super(Facture, self).save(*args, **kwargs)
        if not self.__original_valid and self.valid:
            send_mail_invoice(self)
        if self.is_subscription() \
                and not self.__original_control \
                and self.control \
                and CotisationsOption.get_cached_value('send_voucher_mail'):
            send_mail_voucher(self)

    def __str__(self):
        return str(self.user) + ' ' + str(self.date)


@receiver(post_save, sender=Facture)
def facture_post_save(**kwargs):
    """
    Synchronise the LDAP user after an invoice has been saved.
    """
    facture = kwargs['instance']
    if facture.valid:
        user = facture.user
        user.set_active()
        user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)


@receiver(post_delete, sender=Facture)
def facture_post_delete(**kwargs):
    """
    Synchronise the LDAP user after an invoice has been deleted.
    """
    user = kwargs['instance'].user
    user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)


class CustomInvoice(BaseInvoice):
    recipient = models.CharField(
        max_length=255,
        verbose_name=_("Recipient")
    )
    payment = models.CharField(
        max_length=255,
        verbose_name=_("Payment type")
    )
    address = models.CharField(
        max_length=255,
        verbose_name=_("Address")
    )
    paid = models.BooleanField(
        verbose_name=_("Paid"),
        default=False
    )
    remark = models.TextField(
        verbose_name=_("Remark"),
        blank=True,
        null=True
    )


class CostEstimate(CustomInvoice):
    validity = models.DurationField(
        verbose_name=_("Period of validity"),
        help_text="DD HH:MM:SS"
    )
    final_invoice = models.ForeignKey(
        CustomInvoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="origin_cost_estimate",
        primary_key=False
    )

    def create_invoice(self):
        """Create a CustomInvoice from the CostEstimate."""
        if self.final_invoice is not None:
            return self.final_invoice
        invoice = CustomInvoice()
        invoice.recipient = self.recipient
        invoice.payment = self.payment
        invoice.address = self.address
        invoice.paid = False
        invoice.remark = self.remark
        invoice.date = timezone.now()
        invoice.save()
        self.final_invoice = invoice
        self.save()
        for sale in self.vente_set.all():
            Vente.objects.create(
                facture=invoice,
                name=sale.name,
                prix=sale.prix,
                number=sale.number,
            )
        return invoice

    def can_delete(self, user_request, *args, **kwargs):
        if not user_request.has_perm('cotisations.delete_costestimate'):
            return False, _("You don't have the right "
                            "to delete a cost estimate.")
        if self.final_invoice is not None:
            return False, _("The cost estimate has an "
                            "invoice and can't be deleted.")
        return True, None


# TODO : change Vente to Purchase
class Vente(RevMixin, AclMixin, models.Model):
    """
    The model defining a purchase. It consist of one type of article being
    sold. In particular there may be multiple purchases in a single invoice.

    It's reprensentated by:
        * an amount (the number of items sold)
        * an invoice (whose the purchase is part of)
        * an article
        * (if applicable) a cotisation (which holds some informations about
            the effect of the purchase on the time agreed for this user)
    """

    # TODO : change this to English
    COTISATION_TYPE = (
        ('Connexion', _("Connection")),
        ('Adhesion', _("Membership")),
        ('All', _("Both of them")),
    )

    # TODO : change facture to invoice
    facture = models.ForeignKey(
        'BaseInvoice',
        on_delete=models.CASCADE,
        verbose_name=_("invoice")
    )
    # TODO : change number to amount for clarity
    number = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("amount")
    )
    # TODO : change this field for a ForeinKey to Article
    name = models.CharField(
        max_length=255,
        verbose_name=_("article")
    )
    # TODO : change prix to price
    # TODO : this field is not needed if you use Article ForeignKey
    prix = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("price"))
    # TODO : this field is not needed if you use Article ForeignKey
    duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("duration (in months)")
    )
    # TODO : this field is not needed if you use Article ForeignKey
    type_cotisation = models.CharField(
        choices=COTISATION_TYPE,
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_("subscription type")
    )

    class Meta:
        permissions = (
            ('change_all_vente', _("Can edit all the previous purchases")),
        )
        verbose_name = _("purchase")
        verbose_name_plural = _("purchases")

    # TODO : change prix_total to total_price
    def prix_total(self):
        """
        Returns: the total of price for this amount of items.
        """
        return self.prix*self.number

    def update_cotisation(self):
        """
        Update the related object 'cotisation' if there is one. Based on the
        duration of the purchase.
        """
        if hasattr(self, 'cotisation'):
            cotisation = self.cotisation
            cotisation.date_end = cotisation.date_start + relativedelta(
                months=self.duration*self.number)
        return

    def create_cotis(self, date_start=False):
        """
        Update and create a 'cotisation' related object if there is a
        cotisation_type defined (which means the article sold represents
        a cotisation)
        """
        try:
            invoice = self.facture.facture
        except Facture.DoesNotExist:
            return
        if not hasattr(self, 'cotisation') and self.type_cotisation:
            cotisation = Cotisation(vente=self)
            cotisation.type_cotisation = self.type_cotisation
            if date_start:
                end_cotisation = Cotisation.objects.filter(
                    vente__in=Vente.objects.filter(
                        facture__in=Facture.objects.filter(
                            user=invoice.user
                        ).exclude(valid=False))
                ).filter(
                    Q(type_cotisation='All') |
                    Q(type_cotisation=self.type_cotisation)
                ).filter(
                    date_start__lt=date_start
                ).aggregate(Max('date_end'))['date_end__max']
            elif self.type_cotisation == "Adhesion":
                end_cotisation = invoice.user.end_adhesion()
            else:
                end_cotisation = invoice.user.end_connexion()
            date_start = date_start or timezone.now()
            end_cotisation = end_cotisation or date_start
            date_max = max(end_cotisation, date_start)
            cotisation.date_start = date_max
            cotisation.date_end = cotisation.date_start + relativedelta(
                months=self.duration*self.number
            )
        return

    def save(self, *args, **kwargs):
        """
        Save a purchase object and check if all the fields are coherents
        It also update the associated cotisation in the changes have some
        effect on the user's cotisation
        """
        # Checking that if a cotisation is specified, there is also a duration
        if self.type_cotisation and not self.duration:
            raise ValidationError(
                _("Duration must be specified for a subscription.")
            )
        self.update_cotisation()
        super(Vente, self).save(*args, **kwargs)

    def can_edit(self, user_request, *args, **kwargs):
        if not user_request.has_perm('cotisations.change_vente'):
            return False, _("You don't have the right to edit the purchases.")
        elif (not user_request.has_perm('cotisations.change_all_facture') and
              not self.facture.user.can_edit(
                  user_request, *args, **kwargs
        )[0]):
            return False, _("You don't have the right to edit this user's "
                            "purchases.")
        elif (not user_request.has_perm('cotisations.change_all_vente') and
              (self.facture.control or not self.facture.valid)):
            return False, _("You don't have the right to edit a purchase "
                            "already controlled or invalidated.")
        else:
            return True, None

    def can_delete(self, user_request, *args, **kwargs):
        if not user_request.has_perm('cotisations.delete_vente'):
            return False, _("You don't have the right to delete a purchase.")
        if not self.facture.user.can_edit(user_request, *args, **kwargs)[0]:
            return False, _("You don't have the right to delete this user's "
                            "purchases.")
        if self.facture.control or not self.facture.valid:
            return False, _("You don't have the right to delete a purchase "
                            "already controlled or invalidated.")
        else:
            return True, None

    def can_view(self, user_request, *_args, **_kwargs):
        if (not user_request.has_perm('cotisations.view_vente') and
                self.facture.user != user_request):
            return False, _("You don't have the right to view someone "
                            "else's purchase history.")
        else:
            return True, None

    def __str__(self):
        return str(self.name) + ' ' + str(self.facture)


# TODO : change vente to purchase
@receiver(post_save, sender=Vente)
def vente_post_save(**kwargs):
    """
    Creates a 'cotisation' related object if needed and synchronise the
    LDAP user when a purchase has been saved.
    """
    purchase = kwargs['instance']
    try:
        purchase.facture.facture
    except Facture.DoesNotExist:
        return
    if hasattr(purchase, 'cotisation'):
        purchase.cotisation.vente = purchase
        purchase.cotisation.save()
    if purchase.type_cotisation:
        purchase.create_cotis()
        purchase.cotisation.save()
        user = purchase.facture.facture.user
        user.set_active()
        user.ldap_sync(base=True, access_refresh=True, mac_refresh=False)


# TODO : change vente to purchase
@receiver(post_delete, sender=Vente)
def vente_post_delete(**kwargs):
    """
    Synchronise the LDAP user after a purchase has been deleted.
    """
    purchase = kwargs['instance']
    try:
        invoice = purchase.facture.facture
    except Facture.DoesNotExist:
        return
    if purchase.type_cotisation:
        user = invoice.user
        user.ldap_sync(base=False, access_refresh=True, mac_refresh=False)


class Article(RevMixin, AclMixin, models.Model):
    """
    The definition of an article model. It represents a type of object
    that can be sold to the user.

    It's represented by:
        * a name
        * a price
        * a cotisation type (indicating if this article reprensents a
            cotisation or not)
        * a duration (if it is a cotisation)
        * a type of user (indicating what kind of user can buy this article)
    """

    # TODO : Either use TYPE or TYPES in both choices but not both
    USER_TYPES = (
        ('Adherent', _("Member")),
        ('Club', _("Club")),
        ('All', _("Both of them")),
    )

    COTISATION_TYPE = (
        ('Connexion', _("Connection")),
        ('Adhesion', _("Membership")),
        ('All', _("Both of them")),
    )

    name = models.CharField(
        max_length=255,
        verbose_name=_("designation")
    )
    # TODO : change prix to price
    prix = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("unit price")
    )
    duration = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("duration (in months)")
    )
    type_user = models.CharField(
        choices=USER_TYPES,
        default='All',
        max_length=255,
        verbose_name=_("type of users concerned")
    )
    type_cotisation = models.CharField(
        choices=COTISATION_TYPE,
        default=None,
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_("subscription type")
    )
    available_for_everyone = models.BooleanField(
        default=False,
        verbose_name=_("is available for every user")
    )

    unique_together = ('name', 'type_user')

    class Meta:
        permissions = (
            ('buy_every_article', _("Can buy every article")),
        )
        verbose_name = "article"
        verbose_name_plural = "articles"

    def clean(self):
        if self.name.lower() == 'solde':
            raise ValidationError(
                _("Balance is a reserved article name.")
            )
        if self.type_cotisation and not self.duration:
            raise ValidationError(
                _("Duration must be specified for a subscription.")
            )

    def __str__(self):
        return self.name

    def can_buy_article(self, user, *_args, **_kwargs):
        """Check if a user can buy this article.

        Args:
            self: The article
            user: The user requesting buying

        Returns:
            A boolean stating if usage is granted and an explanation
            message if the boolean is `False`.
        """
        return (
            self.available_for_everyone
            or user.has_perm('cotisations.buy_every_article')
            or user.has_perm('cotisations.add_facture'),
            _("You can't buy this article.")
        )

    @classmethod
    def find_allowed_articles(cls, user, target_user):
        """Finds every allowed articles for an user, on a target user.

        Args:
            user: The user requesting articles.
            target_user: The user to sell articles
        """
        if target_user is None:
            objects_pool = cls.objects.filter(Q(type_user='All'))
        elif target_user.is_class_club:
            objects_pool = cls.objects.filter(
                Q(type_user='All') | Q(type_user='Club')
            )
        else:
            objects_pool = cls.objects.filter(
                Q(type_user='All') | Q(type_user='Adherent')
            )
        if target_user is not None and not target_user.is_adherent():
            objects_pool = objects_pool.filter(
                Q(type_cotisation='All') | Q(type_cotisation='Adhesion')
            )
        if user.has_perm('cotisations.buy_every_article'):
            return objects_pool
        return objects_pool.filter(available_for_everyone=True)


class Banque(RevMixin, AclMixin, models.Model):
    """
    The model defining a bank. It represents a user's bank. It's mainly used
    for statistics by regrouping the user under their bank's name and avoid
    the use of a simple name which leads (by experience) to duplicates that
    only differs by a capital letter, a space, a misspelling, ... That's why
    it's easier to use simple object for the banks.
    """

    name = models.CharField(
        max_length=255,
    )

    class Meta:
        verbose_name = _("bank")
        verbose_name_plural = _("banks")

    def __str__(self):
        return self.name


# TODO : change Paiement to Payment
class Paiement(RevMixin, AclMixin, models.Model):
    """
    The model defining a payment method. It is how the user is paying for the
    invoice. It's easier to know this information when doing the accouts.
    It is represented by:
        * a name
    """

    # TODO : change moyen to method
    moyen = models.CharField(
        max_length=255,
        verbose_name=_("method")
    )
    available_for_everyone = models.BooleanField(
        default=False,
        verbose_name=_("is available for every user")
    )
    is_balance = models.BooleanField(
        default=False,
        editable=False,
        verbose_name=_("is user balance"),
        help_text=_("There should be only one balance payment method."),
        validators=[check_no_balance]
    )

    class Meta:
        permissions = (
            ('use_every_payment', _("Can use every payment method")),
        )
        verbose_name = _("payment method")
        verbose_name_plural = _("payment methods")

    def __str__(self):
        return self.moyen

    def clean(self):
        """l
        Override of the herited clean function to get a correct name
        """
        self.moyen = self.moyen.title()

    def end_payment(self, invoice, request, use_payment_method=True):
        """
        The general way of ending a payment.

        Args:
            invoice: The invoice being created.
            request: Request sent by the user.
            use_payment_method: If this flag is set to True and`self` has
                an attribute `payment_method`, returns the result of
                `self.payment_method.end_payment(invoice, request)`

        Returns:
            An `HttpResponse`-like object.
        """
        payment_method = find_payment_method(self)
        if payment_method is not None and use_payment_method:
            return payment_method.end_payment(invoice, request)

        # So make this invoice valid, trigger send mail
        invoice.valid = True
        invoice.save()

        # In case a cotisation was bought, inform the user, the
        # cotisation time has been extended too
        if any(sell.type_cotisation for sell in invoice.vente_set.all()):
            messages.success(
                request,
                _("The subscription of %(member_name)s was extended to"
                  " %(end_date)s.") % {
                    'member_name': invoice.user.username,
                    'end_date': invoice.user.end_adhesion()
                }
            )
        # Else, only tell the invoice was created
        else:
            messages.success(
                request,
                _("The invoice was created.")
            )
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': invoice.user.pk}
        ))

    def can_use_payment(self, user, *_args, **_kwargs):
        """Check if a user can use this payment.

        Args:
            self: The payment
            user: The user requesting usage
        Returns:
            A boolean stating if usage is granted and an explanation
            message if the boolean is `False`.
        """
        return (
            self.available_for_everyone
            or user.has_perm('cotisations.use_every_payment')
            or user.has_perm('cotisations.add_facture'),
            _("You can't use this payment method.")
        )

    @classmethod
    def find_allowed_payments(cls, user):
        """Finds every allowed payments for an user.

        Args:
            user: The user requesting payment methods.
        """
        if user.has_perm('cotisations.use_every_payment'):
            return cls.objects.all()
        return cls.objects.filter(available_for_everyone=True)

    def get_payment_method_name(self):
        p = find_payment_method(self)
        if p is not None:
            return p._meta.verbose_name
        return _("No custom payment method.")


class Cotisation(RevMixin, AclMixin, models.Model):
    """
    The model defining a cotisation. It holds information about the time a user
    is allowed when he has paid something.
    It characterised by :
        * a date_start (the date when the cotisaiton begins/began
        * a date_end (the date when the cotisation ends/ended
        * a type of cotisation (which indicates the implication of such
            cotisation)
        * a purchase (the related objects this cotisation is linked to)
    """

    COTISATION_TYPE = (
        ('Connexion', _("Connection")),
        ('Adhesion', _("Membership")),
        ('All', _("Both of them")),
    )

    # TODO : change vente to purchase
    vente = models.OneToOneField(
        'Vente',
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("purchase")
    )
    type_cotisation = models.CharField(
        choices=COTISATION_TYPE,
        max_length=255,
        default='All',
        verbose_name=_("subscription type")
    )
    date_start = models.DateTimeField(
        verbose_name=_("start date")
    )
    date_end = models.DateTimeField(
        verbose_name=_("end date")
    )

    class Meta:
        permissions = (
            ('change_all_cotisation', _("Can edit the previous subscriptions")),
        )
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")

    def can_edit(self, user_request, *_args, **_kwargs):
        if not user_request.has_perm('cotisations.change_cotisation'):
            return False, _("You don't have the right to edit a subscription.")
        elif not user_request.has_perm('cotisations.change_all_cotisation') \
                and (self.vente.facture.control or
                     not self.vente.facture.valid):
            return False, _("You don't have the right to edit a subscription "
                            "already controlled or invalidated.")
        else:
            return True, None

    def can_delete(self, user_request, *_args, **_kwargs):
        if not user_request.has_perm('cotisations.delete_cotisation'):
            return False, _("You don't have the right to delete a "
                            "subscription.")
        if self.vente.facture.control or not self.vente.facture.valid:
            return False, _("You don't have the right to delete a subscription "
                            "already controlled or invalidated.")
        else:
            return True, None

    def can_view(self, user_request, *_args, **_kwargs):
        if not user_request.has_perm('cotisations.view_cotisation') and\
                self.vente.facture.user != user_request:
            return False, _("You don't have the right to view someone else's "
                            "subscription history.")
        else:
            return True, None

    def __str__(self):
        return str(self.vente)


@receiver(post_save, sender=Cotisation)
def cotisation_post_save(**_kwargs):
    """
    Mark some services as needing a regeneration after the edition of a
    cotisation. Indeed the membership status may have changed.
    """
    regen('dns')
    regen('dhcp')
    regen('mac_ip_list')
    regen('mailing')


@receiver(post_delete, sender=Cotisation)
def cotisation_post_delete(**_kwargs):
    """
    Mark some services as needing a regeneration after the deletion of a
    cotisation. Indeed the membership status may have changed.
    """
    regen('mac_ip_list')
    regen('mailing')
