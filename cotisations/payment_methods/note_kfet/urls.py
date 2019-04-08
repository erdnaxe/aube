# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Gabriel Detraz

from django.conf.urls import url
from . import views

urlpatterns = [
    url(
        r'^note_payment/(?P<factureid>[0-9]+)$',
        views.note_payment,
        name='note_payment'
    ),
]
