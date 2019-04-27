# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2017  David Sinquin

"""re2o.login
Module in charge of handling the login process and verifications
"""

import binascii
import crypt
import hashlib
import os
from base64 import encodebytes, decodebytes, b64encode, b64decode
from collections import OrderedDict
from hmac import compare_digest as constant_time_compare

from django.contrib.auth import hashers
from django.contrib.auth.backends import ModelBackend

ALGO_LEN = len("{SSHA}$")
DIGEST_LEN = 20


def make_secret(password):
    """ Build a hashed and salted version of the password """
    salt = os.urandom(4)
    h = hashlib.sha1(password.encode())
    h.update(salt)
    return "{SSHA}$" + encodebytes(h.digest() + salt).decode()[:-1]


def hash_nt(password):
    """ Build a md4 hash of the password to use as the NT-password """
    hash_str = hashlib.new('md4', password.encode('utf-16le')).digest()
    return binascii.hexlify(hash_str).upper()


def check_password(challenge_password, password):
    """ Check if a given password match the hash of a stored password """
    challenge_bytes = decodebytes(challenge_password[ALGO_LEN:].encode())
    digest = challenge_bytes[:DIGEST_LEN]
    salt = challenge_bytes[DIGEST_LEN:]
    hr = hashlib.sha1(password.encode())
    hr.update(salt)
    return constant_time_compare(digest, hr.digest())


def hash_password_salt(hashed_password):
    """ Extract the salt from a given hashed password """
    if hashed_password.upper().startswith('{CRYPT}'):
        hashed_password = hashed_password[7:]
        if hashed_password.startswith('$'):
            return '$'.join(hashed_password.split('$')[:-1])
        else:
            return hashed_password[:2]
    elif hashed_password.upper().startswith('{SSHA}'):
        try:
            digest = b64decode(hashed_password[6:])
        except TypeError as error:
            raise ValueError("b64 error for `hashed_password` : %s" % error)
        if len(digest) < 20:
            raise ValueError("`hashed_password` too short")
        return digest[20:]
    elif hashed_password.upper().startswith('{SMD5}'):
        try:
            digest = b64decode(hashed_password[7:])
        except TypeError as error:
            raise ValueError("b64 error for `hashed_password` : %s" % error)
        if len(digest) < 16:
            raise ValueError("`hashed_password` too short")
        return digest[16:]
    else:
        raise ValueError("`hashed_password` should start with '{SSHA}' "
                         "or '{CRYPT}' or '{SMD5}'")


class CryptPasswordHasher(hashers.BasePasswordHasher):
    """
    Crypt password hashing to allow for LDAP auth compatibility
    We do not encode, this should bot be used !
    The actual implementation may depend on the OS.
    """

    algorithm = "{crypt}"

    def encode(self, password, salt):
        pass

    def verify(self, password, encoded):
        """
        Check password against encoded using CRYPT algorithm
        """
        assert encoded.startswith(self.algorithm)
        salt = hash_password_salt(encoded)
        return constant_time_compare(
            self.algorithm + crypt.crypt(password, salt),
            encoded
        )

    def safe_summary(self, encoded):
        """
        Provides a safe summary of the password
        """
        assert encoded.startswith(self.algorithm)
        hash_str = encoded[7:]
        hash_str = binascii.hexlify(decodebytes(hash_str.encode())).decode()
        return OrderedDict([
            ('algorithm', self.algorithm),
            ('iterations', 0),
            ('salt', hashers.mask_hash(hash_str[2 * DIGEST_LEN:], show=2)),
            ('hash', hashers.mask_hash(hash_str[:2 * DIGEST_LEN])),
        ])

    def harden_runtime(self, password, encoded):
        """
        Method implemented to shut up BasePasswordHasher warning

        As we are not using multiple iterations the method is pretty useless
        """
        pass


class MD5PasswordHasher(hashers.BasePasswordHasher):
    """
    Salted MD5 password hashing to allow for LDAP auth compatibility
    We do not encode, this should bot be used !
    """

    algorithm = "{SMD5}"

    def encode(self, password, salt):
        pass

    def verify(self, password, encoded):
        """
        Check password against encoded using SMD5 algorithm
        """
        assert encoded.startswith(self.algorithm)
        salt = hash_password_salt(encoded)
        return constant_time_compare(
            b64encode(hashlib.md5(password.encode() + salt).digest() + salt),
            encoded.encode())

    def safe_summary(self, encoded):
        """
        Provides a safe summary of the password
        """
        assert encoded.startswith(self.algorithm)
        hash_str = encoded[7:]
        hash_str = binascii.hexlify(decodebytes(hash_str.encode())).decode()
        return OrderedDict([
            ('algorithm', self.algorithm),
            ('iterations', 0),
            ('salt', hashers.mask_hash(hash_str[2 * DIGEST_LEN:], show=2)),
            ('hash', hashers.mask_hash(hash_str[:2 * DIGEST_LEN])),
        ])

    def harden_runtime(self, password, encoded):
        """
        Method implemented to shut up BasePasswordHasher warning

        As we are not using multiple iterations the method is pretty useless
        """
        pass


class SSHAPasswordHasher(hashers.BasePasswordHasher):
    """
    Salted SHA-1 password hashing to allow for LDAP auth compatibility
    """

    algorithm = "{SSHA}"

    def encode(self, password, salt):
        """
        Hash and salt the given password using SSHA algorithm

        salt is overridden
        """
        assert password is not None
        return make_secret(password)

    def verify(self, password, encoded):
        """
        Check password against encoded using SSHA algorithm
        """
        assert encoded.startswith(self.algorithm)
        return check_password(encoded, password)

    def safe_summary(self, encoded):
        """
        Provides a safe summary of the password
        """
        assert encoded.startswith(self.algorithm)
        hash_str = encoded[ALGO_LEN:]
        hash_str = binascii.hexlify(decodebytes(hash_str.encode())).decode()
        return OrderedDict([
            ('algorithm', self.algorithm),
            ('iterations', 0),
            ('salt', hashers.mask_hash(hash_str[2 * DIGEST_LEN:], show=2)),
            ('hash', hashers.mask_hash(hash_str[:2 * DIGEST_LEN])),
        ])

    def harden_runtime(self, password, encoded):
        """
        Method implemented to shut up BasePasswordHasher warning

        As we are not using multiple iterations the method is pretty useless
        """
        pass


class RecryptBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # we obtain from the classical auth backend the user
        user = super().authenticate(request, username, password, **kwargs)
        if user:
            if not user.pwd_ntlm:
                # if we dont have NT hash, we create it
                user.pwd_ntlm = hash_nt(password)
                user.save()
            if not ("SSHA" in user.password):
                # if the hash is too old, we update it
                user.password = make_secret(password)
                user.save()
        return user
