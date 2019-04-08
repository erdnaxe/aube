# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""re2o URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home)
    3. Optional: Add a custom name for this URL:
         url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view())
    3. Optional: Add a custom name for this URL:
         url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
    2. Optional: Add a custom namespace for all URL using this urlpatterns:
         url(r'^blog/', include('blog.urls'), namespace='blog')
"""
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from .views import index, about_page, contact_page

handler500 = 're2o.views.handler500'
handler404 = 're2o.views.handler404'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^about/$', about_page, name='about'),
    url(r'^contact/$', contact_page, name='contact'),
    url('^logout/', auth_views.logout, {'next_page': '/'}),
    url('^', include('django.contrib.auth.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', include('users.urls', namespace='users')),
    url(r'^search/', include('search.urls', namespace='search')),
    url(
        r'^cotisations/',
        include('cotisations.urls', namespace='cotisations')
    ),
    url(r'^machines/', include('machines.urls', namespace='machines')),
    url(r'^topologie/', include('topologie.urls', namespace='topologie')),
    url(r'^logs/', include('logs.urls', namespace='logs')),
    url(
        r'^preferences/',
        include('preferences.urls', namespace='preferences')
    ),
]
# Add debug_toolbar URLs if activated
if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
if 'api' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^api/', include('api.urls', namespace='api')),
    ]
