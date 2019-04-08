# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""logs.acl

Here are defined some functions to check acl on the application.
"""
from django.utils.translation import ugettext as _


def can_view(user):
    """Check if an user can view the application.

    Args:
        user: The user who wants to view the application.

    Returns:
        A couple (allowed, msg) where allowed is a boolean which is True if
        viewing is granted and msg is a message (can be None).
    """
    can = user.has_module_perms('admin')
    return can, None if can else _("You don't have the right to view this"
                                   " application.")

