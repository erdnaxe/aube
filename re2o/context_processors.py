# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""Fonction de context, variables renvoyées à toutes les vues"""

from __future__ import unicode_literals

import datetime

from django.contrib import messages
from django.http import HttpRequest
from preferences.models import GeneralOption, OptionalMachine
from django.utils.translation import get_language


def context_user(request):
    """Fonction de context lorsqu'un user est logué (ou non),
    renvoie les infos sur l'user, la liste de ses droits, ses machines"""
    user = request.user
    if get_language()=='fr':
        global_message = GeneralOption.get_cached_value('general_message_fr')
    else:
        global_message = GeneralOption.get_cached_value('general_message_en')
    if global_message:
        if isinstance(request, HttpRequest):
            messages.warning(request, global_message)
        else:
            messages.warning(request._request, global_message)
    if user.is_authenticated():
        interfaces = user.user_interfaces()
    else:
        interfaces = None
    return {
        'request_user': user,
        'interfaces': interfaces,
        'ipv6_enabled': OptionalMachine.get_cached_value('ipv6'),
    }


def date_now(request):
    """Add the current date in the context for quick informations and
    comparisons"""
    return {
        'now_aware': datetime.datetime.now(datetime.timezone.utc),
        'now_naive': datetime.datetime.now()
    }
