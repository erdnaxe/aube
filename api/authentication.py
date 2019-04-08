# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018 Maël Kervella

"""Defines the authentication classes used in the API to authenticate a user.
"""

import datetime

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


class ExpiringTokenAuthentication(TokenAuthentication):
    """Authenticate a user if the provided token is valid and not expired.
    """

    def authenticate_credentials(self, key):
        """See base class. Add the verification the token is not expired.
        """
        base = super(ExpiringTokenAuthentication, self)
        user, token = base.authenticate_credentials(key)

        # Check that the genration time of the token is not too old
        token_duration = datetime.timedelta(
            seconds=settings.API_TOKEN_DURATION
        )
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        if token.created < utc_now - token_duration:
            raise exceptions.AuthenticationFailed(_("The token has expired."))

        return token.user, token
