# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""users.tests
The tests for the Users module.
"""

import os.path

from django.test import TestCase
from django.conf import settings
from . import models

import volatildap


class SchoolTestCase(TestCase):
    def test_school_are_created(self):
        s = models.School.objects.create(name="My awesome school")
        self.assertEqual(s.name, "My awesome school")


class ListShellTestCase(TestCase):
    def test_shell_are_created(self):
        s = models.ListShell.objects.create(shell="/bin/zsh")
        self.assertEqual(s.shell, "/bin/zsh")


class LdapUserTestCase(TestCase):
    def test_create_ldap_user(self):
        g = models.LdapUser.objects.create(
            gid="500",
            name="users_test_ldapuser",
            uid="users_test_ldapuser",
            uidNumber="21001",
            sn="users_test_ldapuser",
            login_shell="/bin/false",
            mail="user@example.net",
            given_name="users_test_ldapuser",
            home_directory="/home/moamoak",
            display_name="users_test_ldapuser",
            dialupAccess="False",
            sambaSID="21001",
            user_password="{SSHA}aBcDeFgHiJkLmNoPqRsTuVwXyZ012345",
            sambat_nt_password="0123456789ABCDEF0123456789ABCDEF",
            macs=[],
            shadowexpire="0"
        )
        self.assertEqual(g.name, 'users_test_ldapuser')


class LdapUserGroupTestCase(TestCase):
    def test_create_ldap_user_group(self):
        g = models.LdapUserGroup.objects.create(
            gid="501",
            members=[],
            name="users_test_ldapusergroup"
        )
        self.assertEqual(g.name, 'users_test_ldapusergroup')


class LdapServiceUserTestCase(TestCase):
    def test_create_ldap_service_user(self):
        g = models.LdapServiceUser.objects.create(
            name="users_test_ldapserviceuser",
            user_password="{SSHA}AbCdEfGhIjKlMnOpQrStUvWxYz987654"
        )
        self.assertEqual(g.name, 'users_test_ldapserviceuser')

