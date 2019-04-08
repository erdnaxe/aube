# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""logs.templatetags.logs_extra
A templatetag to get the class name for a given object
"""

from django import template

register = template.Library()


@register.filter
def classname(obj):
    """ Returns the object class name """
    return obj.__class__.__name__

@register.filter
def is_facture(baseinvoice):
    """Returns True if a baseinvoice has a `Facture` child."""
    return hasattr(baseinvoice, 'facture')

@register.inclusion_tag('buttons/history.html')
def history_button(instance, text=False, html_class=True):
    """Creates the correct history button for an instance.

    Args:
        instance: The instance of which you want to get history buttons.
        text: Flag stating if a 'History' text should be displayed.
        html_class: Flag stating if the link should have the html classes
            allowing it to be displayed as a button.

    """
    return {
        'application': instance._meta.app_label,
        'name': instance._meta.model_name,
        'id': instance.id,
        'text': text,
        'class': html_class,
    }
