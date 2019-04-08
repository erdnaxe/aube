# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018 Maël Kervella

"""Defines the ACL for the whole API.

Importing this module, creates the 'can view api' permission if not already
done.
"""

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _


def _create_api_permission():
    """Creates the 'use_api' permission if not created.
    
    The 'use_api' is a fake permission in the sense it is not associated with an
    existing model and this ensure the permission is created every time this file
    is imported.
    """
    api_content_type, created = ContentType.objects.get_or_create(
        app_label=settings.API_CONTENT_TYPE_APP_LABEL,
        model=settings.API_CONTENT_TYPE_MODEL
    )
    if created:
        api_content_type.save()
    api_permission, created = Permission.objects.get_or_create(
        name=settings.API_PERMISSION_NAME,
        content_type=api_content_type,
        codename=settings.API_PERMISSION_CODENAME
    )
    if created:
        api_permission.save()


_create_api_permission()


def can_view(user):
    """Check if an user can view the application.

    Args:
        user: The user who wants to view the application.

    Returns:
        A couple (allowed, msg) where allowed is a boolean which is True if
        viewing is granted and msg is a message (can be None).
    """
    kwargs = {
        'app_label': settings.API_CONTENT_TYPE_APP_LABEL,
        'codename': settings.API_PERMISSION_CODENAME
    }
    can = user.has_perm('%(app_label)s.%(codename)s' % kwargs)
    return can, None if can else _("You don't have the right to see this"
                                   " application.")
