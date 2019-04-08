# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

from django.core.management.base import BaseCommand, CommandError

from users.models import User


class Command(BaseCommand):
    help = 'Synchronise le ldap à partir du sql. A utiliser dans un cron'

    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument(
            '--full',
            action='store_true',
            dest='full',
            default=False,
            help='Régénération complète du ldap (y compris des machines)',
        )

    def handle(self, *args, **options):
        for usr in User.objects.all():
            usr.ldap_sync(mac_refresh=options['full'])
