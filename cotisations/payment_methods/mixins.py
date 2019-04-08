# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Hugo Levy-Falk


class PaymentMethodMixin:
    """A simple mixin to avoid redefining end_payment if you don't need to"""

    def end_payment(self, invoice, request):
        """Redefine this method in order to get a different ending to the
        payment session if you whish.

        Must return a HttpResponse-like object.
        """
        return self.payment.end_payment(
            invoice, request, use_payment_method=False)
