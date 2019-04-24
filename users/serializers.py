# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2017  Maël Kervella

"""users.serializers
Serializers for the User app
"""

from rest_framework import serializers
from users.models import Club, Adherent


class MailingSerializer(serializers.ModelSerializer):
    """ Serializer to build Mailing objects """

    name = serializers.CharField(source='username')

    class Meta:
        model = Club
        fields = ('name',)


class MailingMemberSerializer(serializers.ModelSerializer):
    """ Serializer fot the Adherent objects (who belong to a
    Mailing) """

    class Meta:
        model = Adherent
        fields = ('email',)
