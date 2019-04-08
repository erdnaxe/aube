# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Hugo Levy-Falk

from django.db import models
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin


class ChequePayment(PaymentMethodMixin, models.Model):
    """
    The model allowing you to pay with a cheque.
    """

    class Meta:
        verbose_name = _("Cheque")

    payment = models.OneToOneField(
        Paiement,
        on_delete=models.CASCADE,
        related_name='payment_method',
        editable=False
    )

    def end_payment(self, invoice, request):
        """Invalidates the invoice then redirect the user towards a view asking
        for informations to add to the invoice before validating it.
        """
        return redirect(reverse(
            'cotisations:cheque:validate',
            kwargs={'invoice_pk': invoice.pk}
        ))

