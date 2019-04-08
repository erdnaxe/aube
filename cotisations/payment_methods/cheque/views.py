# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Hugo Levy-Falk

"""Payment

Here are defined some views dedicated to cheque payement.
"""

from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _

from cotisations.models import Facture as Invoice
from cotisations.utils import find_payment_method

from .models import ChequePayment
from .forms import InvoiceForm


@login_required
def cheque(request, invoice_pk):
    """This view validate an invoice with the data from a cheque."""
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    payment_method = find_payment_method(invoice.paiement)
    if invoice.valid or not isinstance(payment_method, ChequePayment):
        messages.error(
            request,
            _("You can't pay this invoice with a cheque.")
        )
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': request.user.pk}
        ))
    form = InvoiceForm(request.POST or None, instance=invoice)
    if form.is_valid():
        form.instance.valid = True
        form.save()
        return form.instance.paiement.end_payment(
            form.instance,
            request,
            use_payment_method=False
        )
    return render(
        request,
        'cotisations/payment.html',
        {
            'form': form,
            'amount': invoice.prix_total()
        }
    )

