# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""
Urls de l'application preferences, pointant vers les fonctions de views
"""

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'^edit_options/(?P<section>OptionalUser)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>OptionalMachine)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>OptionalTopologie)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>GeneralOption)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>AssoOption)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>HomeOption)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>MailMessageOption)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>RadiusOption)$',
        views.edit_options,
        name='edit-options'
        ),
    url(
        r'^edit_options/(?P<section>CotisationsOption)$',
        views.edit_options,
        name='edit-options'
        ),
    url(r'^add_service/$', views.add_service, name='add-service'),
    url(
        r'^edit_service/(?P<serviceid>[0-9]+)$',
        views.edit_service,
        name='edit-service'
        ),
    url(r'^del_service/(?P<serviceid>[0-9]+)$', views.del_service, name='del-service'),
    url(r'^add_mailcontact/$', views.add_mailcontact, name='add-mailcontact'),
    url(
        r'^edit_mailcontact/(?P<mailcontactid>[0-9]+)$',
        views.edit_mailcontact,
        name='edit-mailcontact'
        ),
    url(r'^del_mailcontact/$', views.del_mailcontact, name='del-mailcontact'),
    url(r'^add_reminder/$', views.add_reminder, name='add-reminder'),
    url(
        r'^edit_reminder/(?P<reminderid>[0-9]+)$',
        views.edit_reminder,
        name='edit-reminder'
        ),
    url(r'^del_reminder/(?P<reminderid>[0-9]+)$', views.del_reminder, name='del-reminder'),
    url(r'^add_radiuskey/$', views.add_radiuskey, name='add-radiuskey'),
    url(
        r'^edit_radiuskey/(?P<radiuskeyid>[0-9]+)$',
        views.edit_radiuskey,
        name='edit-radiuskey'
        ),
    url(r'^del_radiuskey/(?P<radiuskeyid>[0-9]+)$', views.del_radiuskey, name='del-radiuskey'),
    url(r'^add_switchmanagementcred/$', views.add_switchmanagementcred, name='add-switchmanagementcred'),
    url(
        r'^edit_switchmanagementcred/(?P<switchmanagementcredid>[0-9]+)$',
        views.edit_switchmanagementcred,
        name='edit-switchmanagementcred'
        ),
    url(r'^del_switchmanagementcred/(?P<switchmanagementcredid>[0-9]+)$', views.del_switchmanagementcred, name='del-switchmanagementcred'),
    url(
        r'^add_document_template/$',
        views.add_document_template,
        name='add-document-template'
    ),
    url(
        r'^edit_document_template/(?P<documenttemplateid>[0-9]+)$',
        views.edit_document_template,
        name='edit-document-template'
    ),
    url(
        r'^del_document_template/$',
        views.del_document_template,
        name='del-document-template'
    ),
    url(r'^$', views.display_options, name='display-options'),
]
