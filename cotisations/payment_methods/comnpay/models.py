# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2018  Hugo Levy-Falk
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
from django.db import models
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l

from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin

from re2o.aes_field import AESEncryptedField
from .comnpay import Transaction


class ComnpayPayment(PaymentMethodMixin, models.Model):
    """
    The model allowing you to pay with COMNPAY.
    """
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
        verbose_name=_l("ComNpay VAD Number"),
    )
    payment_pass = AESEncryptedField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_l("ComNpay Secret Key"),
    )
    minimum_payment = models.DecimalField(
        verbose_name=_l("Minimum payment"),
        help_text=_l("The minimal amount of money you have to use when paying"
                     " with ComNpay"),
        max_digits=5,
        decimal_places=2,
        default=1,
    )

    def end_payment(self, invoice, request):
        """
        Build a request to start the negociation with Comnpay by using
        a facture id, the price and the secret transaction data stored in
        the preferences.
        """
        invoice.valid = False
        invoice.save()
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
            'action': 'https://secure.homologation.comnpay.com',
            'method': 'POST',
            'content': p.buildSecretHTML(
                _("Pay invoice no : ")+str(invoice.id),
                invoice.prix_total(),
                idTransaction=str(invoice.id)
            ),
            'amount': invoice.prix_total(),
        }
        return render(request, 'cotisations/payment.html', r)

    def check_invoice(self, invoice_form):
        """Checks that a invoice meets the requirement to be paid with ComNpay.

        Args:
            invoice_form: The invoice_form which is to be checked.

        Returns:
            True if the form is valid for ComNpay.

        """
        if invoice_form.instance.prix_total() < self.minimum_payment:
            invoice_form.add_error(
                'paiement',
                _('In order to pay your invoice with ComNpay'
                  ', the price must be grater than {} €')
                .format(self.minimum_payment)
            )
            return False
        return True
