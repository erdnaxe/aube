# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2018  Maël Kervella
# Copyright © 2018  Hugo Levy-Falk

"""
Module defining a AESEncryptedField object that can be used in forms
to handle the use of properly encrypting and decrypting AES keys
"""

import string
import binascii
from random import choice
from Crypto.Cipher import AES

from django.db import models
from django import forms
from django.conf import settings

EOD_asbyte = b'`%EofD%`'  # This should be something that will not occur in strings
EOD = EOD_asbyte.decode('utf-8')

def genstring(length=16, chars=string.printable):
    """ Generate a random string of length `length` and composed of
    the characters in `chars` """
    return ''.join([choice(chars) for i in range(length)])


def encrypt(key, secret):
    """ AES Encrypt a secret with the key `key` """
    obj = AES.new(key)
    datalength = len(secret) + len(EOD)
    if datalength < 16:
        saltlength = 16 - datalength
    else:
        saltlength = 16 - datalength % 16
    encrypted_secret = ''.join([secret, EOD, genstring(saltlength)])
    return obj.encrypt(encrypted_secret)


def decrypt(key, secret):
    """ AES Decrypt a secret with the key `key` """
    obj = AES.new(key)
    uncrypted_secret = obj.decrypt(secret)
    return uncrypted_secret.split(EOD_asbyte)[0]


class AESEncryptedFormField(forms.CharField):
    widget = forms.PasswordInput(render_value=True)


class AESEncryptedField(models.CharField):
    """ A Field that can be used in forms for adding the support
    of AES ecnrypted fields """

    def save_form_data(self, instance, data):
        setattr(instance, self.name, binascii.b2a_base64(
            encrypt(settings.AES_KEY, data)).decode('utf-8'))

    def to_python(self, value):
        if value is None:
            return None
        try:
            return decrypt(settings.AES_KEY, binascii.a2b_base64(value)).decode('utf-8')
        except UnicodeDecodeError as e:
            raise ValueError(
                "Could not decode your field %s, your settings.AES_KEY "
                "is probably wrong." % self.name
            )

    def from_db_value(self, value, *args, **kwargs):
        if value is None:
            return value
        try:
            return decrypt(settings.AES_KEY, binascii.a2b_base64(value)).decode('utf-8')
        except UnicodeDecodeError as e:
            raise ValueError(
                "Could not decode your field %s, your settings.AES_KEY "
                "is probably wrong." % self.name
            )

    def get_prep_value(self, value):
        if value is None:
            return value
        return binascii.b2a_base64(encrypt(settings.AES_KEY, value)).decode('utf-8')

    def formfield(self, **kwargs):
        defaults = {'form_class': AESEncryptedFormField}
        defaults.update(kwargs)
        return super().formfield(**defaults)
