# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2018 Maël Kervella

"""Settings specific to the API.
"""

# RestFramework config for API
REST_FRAMEWORK = {
    'URL_FIELD_NAME': 'api_url',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.authentication.ExpiringTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'api.permissions.AutodetectACLPermission',
    ),
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.PageSizedPagination',
    'PAGE_SIZE': 100
}

# API permission settings
API_CONTENT_TYPE_APP_LABEL = 'api'
API_CONTENT_TYPE_MODEL = 'api'
API_PERMISSION_NAME = 'Can use the API'
API_PERMISSION_CODENAME = 'use_api'

# Activate token authentication
API_APPS = (
    'rest_framework.authtoken',
)

# The expiration time for an authentication token
API_TOKEN_DURATION = 86400  # 24 hours
