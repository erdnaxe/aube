# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Hugo Levy-Falk

from django.db import models
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin

from re2o.aes_field import AESEncryptedField
from .comnpay import Transaction


class ComnpayPayment(PaymentMethodMixin, models.Model):
    """
    The model allowing you to pay with COMNPAY.
    """

    class Meta:
        verbose_name = _("ComNpay")

    payment = models.OneToOneField(
        Paiement,
        on_delete=models.CASCADE,
        related_name='payment_method',
        editable=False
    )
    payment_credential = models.CharField(
        max_length=255,
        default='',
        blank=True,
        verbose_name=_("ComNpay VAT Number"),
    )
    payment_pass = AESEncryptedField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("ComNpay secret key"),
    )
    minimum_payment = models.DecimalField(
        verbose_name=_("Minimum payment"),
        help_text=_("The minimal amount of money you have to use when paying"
                     " with ComNpay"),
        max_digits=5,
        decimal_places=2,
        default=1,
    )
    production = models.BooleanField(
        default=True,
        verbose_name=_("Production mode enabled (production URL, instead of homologation)"),
    )

    def return_url_comnpay(self):
        if self.production:
            return 'https://secure.comnpay.com'
        else:
            return 'https://secure.homologation.comnpay.com'

    def end_payment(self, invoice, request):
        """
        Build a request to start the negociation with Comnpay by using
        a facture id, the price and the secret transaction data stored in
        the preferences.
        """
        host = request.get_host()
        p = Transaction(
            str(self.payment_credential),
            str(self.payment_pass),
            'https://' + host + reverse(
                'cotisations:comnpay:accept_payment',
                kwargs={'factureid': invoice.id}
            ),
            'https://' + host + reverse('cotisations:comnpay:refuse_payment'),
            'https://' + host + reverse('cotisations:comnpay:ipn'),
            "",
            "D"
        )

        r = {
            'action': self.return_url_comnpay(),
            'method': 'POST',
            'content': p.buildSecretHTML(
                _("Pay invoice number ")+str(invoice.id),
                invoice.prix_total(),
                idTransaction=str(invoice.id)
            ),
            'amount': invoice.prix_total(),
        }
        return render(request, 'cotisations/payment.html', r)

    def check_price(self, price, *args, **kwargs):
        """Checks that the price meets the requirement to be paid with ComNpay.
        """
        return ((price >= self.minimum_payment),
                _("In order to pay your invoice with ComNpay, the price must"
                  " be greater than {} €.").format(self.minimum_payment))

