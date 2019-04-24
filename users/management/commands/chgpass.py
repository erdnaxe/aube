# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Lev-Arcady Sellem

import os
import pwd

from django.core.management.base import BaseCommand, CommandError
from users.forms import PassForm
from re2o.script_utils import get_user, get_system_user, form_cli


class Command(BaseCommand):
    help = "Changer le mot de passe d'un utilisateur"

    def add_arguments(self, parser):
        parser.add_argument('target_username', nargs='?')

    def handle(self, *args, **kwargs):

        current_username = get_system_user()
        current_user = get_user(current_username)
        target_username = kwargs["target_username"] or current_username
        target_user = get_user(target_username)

        ok, msg = target_user.can_change_password(current_user)
        if not ok:
            raise CommandError(msg)

        self.stdout.write(
            "Changement du mot de passe de %s" % target_user.username
        )

        form_cli(
            PassForm,
            current_user,
            "Changement du mot de passe",
            instance=target_user
        )
