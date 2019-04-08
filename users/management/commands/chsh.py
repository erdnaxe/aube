# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Jean-Baptiste Daval

import os
import sys
import pwd

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from reversion import revisions as reversion

from users.models import User, ListShell
from re2o.script_utils import get_user, get_system_user


class Command(BaseCommand):
    help = 'Change the default shell of a user'

    def add_arguments(self, parser):
        parser.add_argument('target_username', nargs='?')

    def handle(self, *args, **options):

        current_username = get_system_user()
        current_user = get_user(current_username)

        target_username = options["target_username"] or current_username
        target_user = get_user(target_username)

        # L'utilisateur n'a pas le droit de changer le shell
        ok, msg = target_user.can_change_shell(current_user)
        if not ok:
            raise CommandError(msg)

        shells = ListShell.objects.all()

        current_shell = "inconnu"
        if target_user.shell:
            current_shell = target_user.shell.get_pretty_name()
        self.stdout.write(
            "Choisissez un shell pour l'utilisateur %s (le shell actuel est "
            "%s) :" % (target_user.pseudo, current_shell)
        )
        for shell in shells:
            self.stdout.write("%d - %s (%s)" % (
                shell.id,
                shell.get_pretty_name(),
                shell.shell
            ))
        shell_id = input("Entrez un nombre : ")

        try:
            shell_id = int(shell_id)
        except:
            raise CommandError("Choix invalide")

        shell = ListShell.objects.filter(id=shell_id)
        if not shell:
            raise CommandError("Choix invalide")

        target_user.shell = shell.first()
        with transaction.atomic(), reversion.create_revision():
            target_user.save()
            reversion.set_user(current_user)
            reversion.set_comment("Shell modifié")

        self.stdout.write(self.style.SUCCESS(
            "Shell modifié. La modification peut prendre quelques minutes "
            "pour s'appliquer."
        ))
