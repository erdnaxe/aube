# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Hugo Levy-Falk

from django.conf.urls import include, url
from . import comnpay, cheque, note_kfet

urlpatterns = [
    url(r'^comnpay/', include(comnpay.urls, namespace='comnpay')),
    url(r'^cheque/', include(cheque.urls, namespace='cheque')),
    url(r'^note_kfet/', include(note_kfet.urls, namespace='note_kfet')),
]
