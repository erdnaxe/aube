# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Maël Kervella

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(needs_autoescape=False)
def tick(valeur, autoescape=False):

    if isinstance(valeur,bool):
        if valeur == True:
            result = '<i style="color: #1ECA18;" class="fa fa-check"></i>'
        else:
            result = '<i style="color: #D10115;" class="fa fa-times"></i>'
        return mark_safe(result)

    else: #  if the value is not a boolean, display it as if tick was not called 
        return valeur
