# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""users
The app managing everything related to the users such as personal
informations or the right groups.
This is probably the most central app. It is strongly linked with
all the other because a user has devices (machines), a cotisation
(cotisations), a room (topologie)
"""

from .acl import *
