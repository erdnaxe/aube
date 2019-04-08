# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""re2o.templatetags.self_adhesion
A simple templatagetag which returns the value of the option `self_adhesion`
which indicated if a user can creates an account by himself
"""

from django import template
from preferences.models import OptionalUser


register = template.Library()


@register.simple_tag
def self_adhesion():
    """ Returns True if the user are allowed to create accounts """
    options, _created = OptionalUser.objects.get_or_create()
    return options.self_adhesion
