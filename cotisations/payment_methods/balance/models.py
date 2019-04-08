# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Hugo Levy-Falk

from django.contrib import messages
from django.db import models
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin


class BalancePayment(PaymentMethodMixin, models.Model):
    """
    The model allowing you to pay with a cheque.
    """

    class Meta:
        verbose_name = _("user balance")

    payment = models.OneToOneField(
        Paiement,
        on_delete=models.CASCADE,
        related_name='payment_method',
        editable=False
    )
    minimum_balance = models.DecimalField(
        verbose_name=_("Minimum balance"),
        help_text=_("The minimal amount of money allowed for the balance"
                     " at the end of a payment. You can specify negative "
                     "amount."
                     ),
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    maximum_balance = models.DecimalField(
        verbose_name=_("Maximum balance"),
        help_text=_("The maximal amount of money allowed for the balance."),
        max_digits=5,
        decimal_places=2,
        default=50,
        blank=True,
        null=True,
    )
    credit_balance_allowed = models.BooleanField(
        verbose_name=_("Allow user to credit their balance"),
        default=False,
    )

    def end_payment(self, invoice, request):
        """Changes the user's balance to pay the invoice. If it is not
        possible, shows an error and invalidates the invoice.
        """
        user = invoice.user
        total_price = invoice.prix_total()
        if user.solde - total_price < self.minimum_balance:
            messages.error(
                request,
                _("Your balance is too low for this operation.")
            )
            return redirect(reverse(
                'users:profil',
                kwargs={'userid': user.id}
            ))
        return invoice.paiement.end_payment(
            invoice,
            request,
            use_payment_method=False
        )

    def valid_form(self, form):
        """Checks that there is not already a balance payment method."""
        p = Paiement.objects.filter(is_balance=True)
        if len(p) > 0:
            form.add_error(
                'payment_method',
                _("There is already a payment method for user balance.")
            )

    def alter_payment(self, payment):
        """Register the payment as a balance payment."""
        self.payment.is_balance = True

    def check_price(self, price, user, *args, **kwargs):
        """Checks that the price meets the requirement to be paid with user
        balance.
        """
        return (
            user.solde - price >= self.minimum_balance,
            _("Your balance is too low for this operation.")
        )

    def can_credit_balance(self, user_request):
        return (
            len(Paiement.find_allowed_payments(user_request)
                .exclude(is_balance=True)) > 0
        ) and self.credit_balance_allowed

