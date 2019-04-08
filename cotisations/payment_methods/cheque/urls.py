# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Hugo Levy-Falk

from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^validate/(?P<invoice_pk>[0-9]+)$',
        views.cheque,
        name='validate'
    )
]
