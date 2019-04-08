# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

from django.core.management.base import BaseCommand, CommandError

from users.models import User
from cotisations.models import Facture
from preferences.models import OptionalUser
from datetime import timedelta

from django.utils import timezone

class Command(BaseCommand):
    help = "Delete non members users (not yet active)"

    def handle(self, *args, **options):
        """First deleting invalid invoices, and then deleting the users"""
        days = OptionalUser.get_cached_value('delete_notyetactive')
        users_to_delete = User.objects.filter(state=User.STATE_NOT_YET_ACTIVE).filter(registered__lte=timezone.now() - timedelta(days=days)).exclude(facture__valid=True).distinct()
        print("Deleting " + str(users_to_delete.count()) + " users")
        Facture.objects.filter(user__in=users_to_delete).delete()
        users_to_delete.delete()
