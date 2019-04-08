# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Pierre-Antoine Comby
# Copyright © 2018  Gabriel Detraz

"""
This module contains a method to pay online using comnpay.
"""
from . import models, urls
NAME = "NOTE"
PaymentMethod = models.NotePayment
