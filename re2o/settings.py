# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""
Django settings for re2o project.

Generated by 'django-admin startproject' using Django 1.8.13.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

from __future__ import unicode_literals

import os
from .settings_local import *
from django.utils.translation import ugettext_lazy as _

# The root directory for the project
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Auth definition
PASSWORD_HASHERS = (
    're2o.login.SSHAPasswordHasher',
    're2o.login.MD5PasswordHasher',
    're2o.login.CryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
)
AUTH_USER_MODEL = 'users.User'  # The class to use for authentication
LOGIN_URL = '/login/'           # The URL for login page
LOGIN_REDIRECT_URL = '/'        # The URL for redirecting after login

# Application definition
DJANGO_CONTRIB_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)
EXTERNAL_CONTRIB_APPS = (
    'bootstrap3',
    'rest_framework',
    'reversion',
)
LOCAL_APPS = (
    'users',
    'machines',
    'cotisations',
    'topologie',
    'search',
    're2o',
    'preferences',
    'logs',
)
INSTALLED_APPS = (
    DJANGO_CONTRIB_APPS +
    EXTERNAL_CONTRIB_APPS +
    LOCAL_APPS +
    OPTIONNAL_APPS
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'reversion.middleware.RevisionMiddleware',
)

AUTHENTICATION_BACKENDS = ['re2o.login.RecryptBackend']

# Include debug_toolbar middleware if activated
if 'debug_toolbar' in INSTALLED_APPS:
    # Include this middleware at the beggining
    MIDDLEWARE_CLASSES = (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ) + MIDDLEWARE_CLASSES
    # Change the default show_toolbar middleware
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': 're2o.middleware.show_debug_toolbar'
    }

# The root url module to define the project URLs
ROOT_URLCONF = 're2o.urls'

# The templates configuration (see Django documentation)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # Use only absolute paths with '/' delimiters even on Windows
            os.path.join(BASE_DIR, 'templates').replace('\\', '/'),
            os.path.join(BASE_DIR, 'media', 'templates').replace('\\', '/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                're2o.context_processors.context_user',
                're2o.context_processors.date_now',
            ],
        },
    },
]

# The WSGI module to use in a server environment
WSGI_APPLICATION = 're2o.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = 'en'
USE_I18N = True
USE_L10N = True
# Proritary location search for translations
# then searches in {app}/locale/ for app in INSTALLED_APPS
# Use only absolute paths with '/' delimiters even on Windows
LOCALE_PATHS = [
    # For translations outside of apps
    os.path.join(BASE_DIR, 'templates', 'locale').replace('\\', '/')
]
LANGUAGES = [
    ('en', _('English')),
    ('fr', _('French'))
]

# Should use time zone ?
USE_TZ = True

# Router config for database
DATABASE_ROUTERS = ['ldapdb.router.Router']

# django-bootstrap3 config
BOOTSTRAP3 = {
    'jquery_url': '/javascript/jquery/jquery.min.js',
    'base_url': '/javascript/bootstrap/',
    'include_jquery': True,
}
BOOTSTRAP_BASE_URL = '/javascript/bootstrap/'

# Directories where collectstatic should look for static files
# Use only absolute paths with '/' delimiters even on Windows
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static').replace('\\', '/'),
    "/usr/share/fonts-font-awesome/",
)
# Directory where the static files served by the server are stored
STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')
# The URL to access the static files
STATIC_URL = '/static/'
# Directory where the media files served by the server are stored
MEDIA_ROOT = os.path.join(BASE_DIR, 'media').replace('\\', '/')
# The URL to access the static files
MEDIA_URL = os.path.join(BASE_DIR,'/media/')

# Models to use for graphs
GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}

# Activate API
if 'api' in INSTALLED_APPS:
    from api.settings import *
    INSTALLED_APPS += API_APPS
