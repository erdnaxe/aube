# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Hugo Levy-Falk

from django import forms

from re2o.mixins import FormRevMixin
from cotisations.models import Facture as Invoice


class InvoiceForm(FormRevMixin, forms.ModelForm):
    """A simple form to get the bank a the cheque number."""
    class Meta:
        model = Invoice
        fields = ['banque', 'cheque']
