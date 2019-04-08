# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018 Maël Kervella

"""Defines the middlewares used in all apps of re2o.
"""

from django.conf import settings


def show_debug_toolbar(request):
    """Middleware to determine wether to show the toolbar.

    Compared to `django-debug-toolbar`'s default, add the possibility to allow
    any IP to see the debug panel by not setting the `INTERNAL_IPS` options

    Args:
        requests: The request object that must be checked.

    Returns:
        The boolean indicating if the debug toolbar should be shown.
    """
    if hasattr(settings, 'INTERNAL_IPS') and settings.INTERNAL_IPS and \
            request.META.get('REMOTE_ADDR', None) not in settings.INTERNAL_IPS:
        return False

    return bool(settings.DEBUG)
