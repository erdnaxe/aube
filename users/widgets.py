# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later

from django.forms.widgets import Input
from django.forms.utils import flatatt 
from django.utils.safestring import mark_safe 
from django.template import Context, Template 
from django.template.loader import get_template 
from django.conf import settings 
from django.utils.translation import ugettext_lazy as _, get_language_bidi 
from django.utils.dates import ( 
    WEEKDAYS, 
    WEEKDAYS_ABBR, 
    MONTHS, 
    MONTHS_3, 
    MONTHS_AP, 
    MONTHS_ALT 
)

def list2str(str_iterable):
    """
    Utility function to return a string representing a list of string 

    :params str_iterable: An iterable object where each element is of type str
    :returns: A representation of the iterable as a list (e.g '["a", "b"]')
    """
    return '["' + '", "'.join(str_iterable) + '"]'
    
class DateTimePicker(Input):
    is_localized = False
    def render(self, name, value, attrs=None): 
        super().render(name, value, attrs) 
        flat_attrs = flatatt(attrs)
        context = {
            'name': name,
            'attrs': flat_attrs, 
            'id': attrs['id'], 
            'closeText': _("Close"), 
            'currentText': _("Today"),
            'dayNames': mark_safe(list2str((str(item[1]) for item in WEEKDAYS.items()))),
            'dayNamesMin': mark_safe(list2str((str(item[1]) for item in WEEKDAYS_ABBR.items()))), 
            'dayNamesShort': mark_safe(list2str((str(item[1]) for item in WEEKDAYS_ABBR.items()))), 
            'firstDay': mark_safe('"' + str(WEEKDAYS[settings.FIRST_DAY_OF_WEEK]) + '"'), 
            'isRTL': str(get_language_bidi()).lower(), 
            'monthNames': mark_safe(list2str((str(item[1]) for item in MONTHS.items()))),
            'monthNamesShort': mark_safe(list2str((str(item[1]) for item in MONTHS_3.items()))), 
            'nextText': mark_safe('"' + str(_('Next')) + '"'), 
            'prevText': mark_safe('"' + str(_('Previous')) + '"'), 
            'weekHeader': mark_safe('"' + str(_('Wk')) + '"' ),
        }
        template = get_template('users/datetimepicker.html')
        return template.render(context) 

