# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Hugo Levy-Falk

from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^accept/(?P<factureid>[0-9]+)$',
        views.accept_payment,
        name='accept_payment'
    ),
    url(
        r'^refuse/$',
        views.refuse_payment,
        name='refuse_payment'
    ),
    url(
        r'^ipn/$',
        views.ipn,
        name='ipn'
    ),
]
