# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""URL Router"""

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .views import index, about_page, contact_page

# Admin site configuration
admin.site.index_title = _('Homepage')
admin.site.index_template = 'index.html'

handler500 = 're2o.views.handler500'
handler404 = 're2o.views.handler404'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^about/$', about_page, name='about'),
    url(r'^contact/$', contact_page, name='contact'),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^manage/', include(admin.site.urls)),
    url(r'^doc/', include('django.contrib.admindocs.urls')),
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
