# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""
WSGI config for re2o project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

from __future__ import unicode_literals

import os
from os.path import dirname
import sys

from django.core.wsgi import get_wsgi_application


sys.path.append(dirname(dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "re2o.settings")

application = get_wsgi_application()
