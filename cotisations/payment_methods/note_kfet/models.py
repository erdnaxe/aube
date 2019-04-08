# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Pierre-Antoine Comby
# Copyright © 2018  Gabriel Detraz

from django.db import models
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from cotisations.models import Paiement
from cotisations.payment_methods.mixins import PaymentMethodMixin

from django.shortcuts import render, redirect


class NotePayment(PaymentMethodMixin, models.Model):
    """
    The model allowing you to pay with NoteKfet2015.
    """

    class Meta:
        verbose_name = _("NoteKfet")

    payment = models.OneToOneField(
        Paiement,
        on_delete = models.CASCADE,
        related_name = 'payment_method',
        editable = False
    )
    server = models.CharField(
        max_length=255,
        verbose_name=_("server")
    )
    port = models.PositiveIntegerField(
        blank = True,
        null = True
    )
    id_note = models.PositiveIntegerField(
        blank = True,
        null = True
    )

    def end_payment(self, invoice, request):
        return redirect(reverse(
            'cotisations:note_kfet:note_payment',
            kwargs={'factureid': invoice.id}
        ))
