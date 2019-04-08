# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""
Definition des urls, pointant vers les views
"""

from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^new_user/$', views.new_user, name='new-user'),
    url(r'^new_club/$', views.new_club, name='new-club'),
    url(r'^edit_info/(?P<userid>[0-9]+)$', views.edit_info, name='edit-info'),
    url(r'^edit_club_admin_members/(?P<clubid>[0-9]+)$',
        views.edit_club_admin_members,
        name='edit-club-admin-members'),
    url(r'^state/(?P<userid>[0-9]+)$', views.state, name='state'),
    url(r'^groups/(?P<userid>[0-9]+)$', views.groups, name='groups'),
    url(r'^password/(?P<userid>[0-9]+)$', views.password, name='password'),
    url(r'^del_group/(?P<userid>[0-9]+)/(?P<listrightid>[0-9]+)$',
        views.del_group,
        name='del-group'),
    url(r'^del_superuser/(?P<userid>[0-9]+)$',
        views.del_superuser,
        name='del-superuser'),
    url(r'^new_serviceuser/$', views.new_serviceuser, name='new-serviceuser'),
    url(r'^edit_serviceuser/(?P<serviceuserid>[0-9]+)$',
        views.edit_serviceuser,
        name='edit-serviceuser'),
    url(r'^del_serviceuser/(?P<serviceuserid>[0-9]+)$',
        views.del_serviceuser,
        name='del-serviceuser'),
    url(r'^add_ban/(?P<userid>[0-9]+)$', views.add_ban, name='add-ban'),
    url(r'^edit_ban/(?P<banid>[0-9]+)$', views.edit_ban, name='edit-ban'),
    url(r'^del-ban/(?P<banid>[0-9]+)$', views.del_ban, name='del-ban'),
    url(r'^add_whitelist/(?P<userid>[0-9]+)$',
        views.add_whitelist,
        name='add-whitelist'),
    url(r'^edit_whitelist/(?P<whitelistid>[0-9]+)$',
        views.edit_whitelist,
        name='edit-whitelist'),
    url(r'^del_whitelist/(?P<whitelistid>[0-9]+)$',
        views.del_whitelist,
        name='del-whitelist'),
    url(r'^add_emailaddress/(?P<userid>[0-9]+)$',
        views.add_emailaddress,
        name='add-emailaddress'),
    url(r'^edit_emailaddress/(?P<emailaddressid>[0-9]+)$',
        views.edit_emailaddress,
        name='edit-emailaddress'),
    url(r'^del_emailaddress/(?P<emailaddressid>[0-9]+)$',
        views.del_emailaddress,
        name='del-emailaddress'),
    url(r'^edit_email_settings/(?P<userid>[0-9]+)$',
        views.edit_email_settings,
        name='edit-email-settings'),
    url(r'^add_school/$', views.add_school, name='add-school'),
    url(r'^edit_school/(?P<schoolid>[0-9]+)$',
        views.edit_school,
        name='edit-school'),
    url(r'^del_school/$', views.del_school, name='del-school'),
    url(r'^add_listright/$', views.add_listright, name='add-listright'),
    url(r'^edit_listright/(?P<listrightid>[0-9]+)$',
        views.edit_listright,
        name='edit-listright'),
    url(r'^del_listright/$', views.del_listright, name='del-listright'),
    url(r'^add_shell/$', views.add_shell, name='add-shell'),
    url(r'^edit_shell/(?P<listshellid>[0-9]+)$',
        views.edit_shell,
        name='edit-shell'),
    url(r'^del_shell/(?P<listshellid>[0-9]+)$',
        views.del_shell,
        name='del-shell'),
    url(r'^profil/(?P<userid>[0-9]+)$', views.profil, name='profil'),
    url(r'^index_ban/$', views.index_ban, name='index-ban'),
    url(r'^index_white/$', views.index_white, name='index-white'),
    url(r'^index_school/$', views.index_school, name='index-school'),
    url(r'^index_shell/$', views.index_shell, name='index-shell'),
    url(r'^index_listright/$', views.index_listright, name='index-listright'),
    url(r'^index_serviceusers/$',
        views.index_serviceusers,
        name='index-serviceusers'),
    url(r'^mon_profil/$', views.mon_profil, name='mon-profil'),
    url(r'^process/(?P<token>[a-z0-9]{32})/$', views.process, name='process'),
    url(r'^reset_password/$', views.reset_password, name='reset-password'),
    url(r'^mass_archive/$', views.mass_archive, name='mass-archive'),
    url(r'^$', views.index, name='index'),
    url(r'^index_clubs/$', views.index_clubs, name='index-clubs'),
    url(r'^initial_register/$', views.initial_register, name='initial-register'),
    url(r'^rest/ml/std/$',
        views.ml_std_list,
        name='ml-std-list'),
    url(r'^rest/ml/std/member/(?P<ml_name>\w+)/$',
        views.ml_std_members,
        name='ml-std-members'),
    url(r'^rest/ml/club/$',
        views.ml_club_list,
        name='ml-club-list'),
    url(r'^rest/ml/club/admin/(?P<ml_name>\w+)/$',
        views.ml_club_admins,
        name='ml-club-admins'),
    url(r'^rest/ml/club/member/(?P<ml_name>\w+)/$',
        views.ml_club_members,
        name='ml-club-members'),
]
