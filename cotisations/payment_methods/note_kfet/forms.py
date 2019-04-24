# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Pierre-Antoine Comby
# Copyright © 2018  Gabriel Detraz

from django import forms
from django.utils.translation import ugettext_lazy as _

from cotisations.utils import find_payment_method

class NoteCredentialForm(forms.Form):
    """A special form to get credential to connect to a NoteKfet2015 server throught his API
    object.
    """
    login = forms.CharField(
            label=_("username note")
        )
    password = forms.CharField(
            label=_("Password"),
            widget=forms.PasswordInput
        )
   
