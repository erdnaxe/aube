# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Benjamin Graillot
# Copyright © 2013-2015 Raphaël-David Lasseri <lasseri@crans.org>

import sys
import re
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import make_aware

from users.models import User

# Une liste d'expressions régulières à chercher dans les logs.
# Elles doivent contenir un groupe 'date' et un groupe 'user'.
# Pour le CAS on prend comme entrée
# cat ~/cas.log | grep -B 2 -A 2 "ACTION: AUTHENTICATION_SUCCESS"| grep 'WHEN\|WHO'|sed 'N;s/\n/ /'
COMPILED_REGEX = map(re.compile, [
    r'^(?P<date>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}).*(?:'r'dovecot.*Login: user=<|'r'sshd.*Accepted.*for 'r')(?P<user>[^ >]+).*$',
    r'^(?P<date>.*) LOGIN INFO User logged in : (?P<user>.*)',
    r'WHO: \[username: (?P<user>.*)\] WHEN: (?P<date>.* CET .*)',
    r'WHO: \[username: (?P<user>.*)\] WHEN: (?P<date>.* CEST .*)'
])

# Les formats de date en strftime associés aux expressions ci-dessus.
DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%d/%b/%Y:%H:%M:%S",
    "%a %b %d CET %H:%M:%S%Y",
    "%a %b %d CEST %H:%M:%S%Y"
]


class Command(BaseCommand):
    help = ('Update the time of the latest connection for users by matching '
            'stdin against a set of regular expressions')

    def handle(self, *args, **options):

        def parse_logs(logfile):
            """
            Parse les logs sur l'entrée standard et rempli un dictionnaire
            ayant pour clef le username de l'adherent
            """
            global COMPILED_REGEX, DATE_FORMATS

            parsed_log = {}
            for line in logfile:
                for i, regex in enumerate(COMPILED_REGEX):
                    m = regex.match(line)
                    if m:
                        parsed_log[m.group('user')] = make_aware(
                            datetime.strptime(m.group('date'), DATE_FORMATS[i])
                        )
            return parsed_log

        parsed_log = parse_logs(sys.stdin)

        for username in parsed_log:
            for user in User.objects.filter(username=username):
                last_login = parsed_log.get(user.username, user.last_login)
                if not user.last_login:
                    user.last_login = last_login
                elif last_login > user.last_login:
                    user.last_login = last_login
                user.save()
