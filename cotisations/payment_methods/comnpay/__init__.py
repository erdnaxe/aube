# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Hugo Levy-Falk

"""
This module contains a method to pay online using comnpay.
"""
from . import models, urls, views
NAME = "COMNPAY"
PaymentMethod = models.ComnpayPayment
