# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018  Lev-Arcady Sellem

"""re2o.script_utils
A set of utility scripts that can be used as standalone to interact easily
with Re2o throught the CLI
"""

import os
from os.path import dirname
import sys
import pwd

from getpass import getpass
from reversion import revisions as reversion

from django.core.wsgi import get_wsgi_application
from django.core.management.base import CommandError
from django.db import transaction
from django.utils.html import strip_tags

from users.models import User

proj_path = dirname(dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re2o.settings")
sys.path.append(proj_path)
os.chdir(proj_path)

application = get_wsgi_application()


def get_user(pseudo):
    """Cherche un utilisateur re2o à partir de son pseudo"""
    user = User.objects.filter(pseudo=pseudo)
    if len(user) == 0:
        raise CommandError("Invalid user.")
    if len(user) > 1:
        raise CommandError("Several users match this username. This SHOULD"
                           " NOT happen.")
    return user[0]


def get_system_user():
    """Retourne l'utilisateur système ayant lancé la commande"""
    return pwd.getpwuid(int(os.getenv("SUDO_UID") or os.getuid())).pw_name


def form_cli(Form, user, action, *args, **kwargs):
    """
    Remplit un formulaire à partir de la ligne de commande
        Form : le formulaire (sous forme de classe) à remplir
        user : l'utilisateur re2o faisant la modification
        action : l'action réalisée par le formulaire (pour les logs)
    Les arguments suivants sont transmis tels quels au formulaire.
    """
    data = {}
    dumb_form = Form(user=user, *args, **kwargs)
    for key in dumb_form.fields:
        if not dumb_form.fields[key].widget.input_type == 'hidden':
            if dumb_form.fields[key].widget.input_type == 'password':
                data[key] = getpass("%s : " % dumb_form.fields[key].label)
            else:
                data[key] = input("%s : " % dumb_form.fields[key].label)

    form = Form(data, user=user, *args, **kwargs)
    if not form.is_valid():
        sys.stderr.write("Errors: \n")
        for err in form.errors:
            # Oui, oui, on gère du HTML là où d'autres ont eu la
            # lumineuse idée de le mettre
            sys.stderr.write(
                "\t%s : %s\n" % (err, strip_tags(form.errors[err]))
            )
        raise CommandError("Invalid form.")

    with transaction.atomic(), reversion.create_revision():
        form.save()
        reversion.set_user(user)
        reversion.set_comment(action)

    sys.stdout.write("%s : done. The edit may take several minutes to"
                     " apply.\n" % action)
