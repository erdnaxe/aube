# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""
Urls de l'application logs, pointe vers les fonctions de views.
Inclu dans le re2o.urls
"""
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^stats_logs$', views.stats_logs, name='stats-logs'),
    url(r'^revert_action/(?P<revision_id>[0-9]+)$',
        views.revert_action,
        name='revert-action'),
    url(r'^stats_general/$', views.stats_general, name='stats-general'),
    url(r'^stats_models/$', views.stats_models, name='stats-models'),
    url(r'^stats_users/$', views.stats_users, name='stats-users'),
    url(r'^stats_actions/$', views.stats_actions, name='stats-actions'),
    url(
        r'(?P<application>\w+)/(?P<object_name>\w+)/(?P<object_id>[0-9]+)$',
        views.history,
        name='history',
    ),
]
