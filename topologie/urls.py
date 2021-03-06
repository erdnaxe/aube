# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""
Definition des urls de l'application topologie.
Inclu dans urls de re2o.

Fait référence aux fonctions du views
"""

from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index_ap/$', views.index_ap, name='index-ap'),
    url(r'^new_ap/$', views.new_ap, name='new-ap'),
    url(r'^edit_ap/(?P<accesspointid>[0-9]+)$',
        views.edit_ap,
        name='edit-ap'),
    url(r'^create_ports/(?P<switchid>[0-9]+)$',
        views.create_ports,
        name='create-ports'),
    url(r'^new_switch/$', views.new_switch, name='new-switch'),
    url(r'^switch/(?P<switchid>[0-9]+)$',
        views.index_port,
        name='index-port'),
    url(r'^edit_port/(?P<portid>[0-9]+)$', views.edit_port, name='edit-port'),
    url(r'^new_port/(?P<switchid>[0-9]+)$', views.new_port, name='new-port'),
    url(r'^del_port/(?P<portid>[0-9]+)$', views.del_port, name='del-port'),
    url(r'^edit_switch/(?P<switchid>[0-9]+)$',
        views.edit_switch,
        name='edit-switch'),
    url(r'^new_stack/$', views.new_stack, name='new-stack'),
    url(r'^index_physical_grouping/$',
        views.index_physical_grouping,
        name='index-physical-grouping'),
    url(r'^edit_stack/(?P<stackid>[0-9]+)$',
        views.edit_stack,
        name='edit-stack'),
    url(r'^del_stack/(?P<stackid>[0-9]+)$',
        views.del_stack,
        name='del-stack'),
    url(r'^index_model_switch/$',
        views.index_model_switch,
        name='index-model-switch'),
    url(r'^index_model_switch/$',
        views.index_model_switch,
        name='index-model-switch'),
    url(r'^new_model_switch/$',
        views.new_model_switch,
        name='new-model-switch'),
    url(r'^edit_model_switch/(?P<modelswitchid>[0-9]+)$',
        views.edit_model_switch,
        name='edit-model-switch'),
    url(r'^del_model_switch/(?P<modelswitchid>[0-9]+)$',
        views.del_model_switch,
        name='del-model-switch'),
    url(r'^new_constructor_switch/$',
        views.new_constructor_switch,
        name='new-constructor-switch'),
    url(r'^edit_constructor_switch/(?P<constructorswitchid>[0-9]+)$',
        views.edit_constructor_switch,
        name='edit-constructor-switch'),
    url(r'^del_constructor_switch/(?P<constructorswitchid>[0-9]+)$',
        views.del_constructor_switch,
        name='del-constructor-switch'),
    url(r'^new_switch_bay/$',
        views.new_switch_bay,
        name='new-switch-bay'),
    url(r'^edit_switch_bay/(?P<switchbayid>[0-9]+)$',
        views.edit_switch_bay,
        name='edit-switch-bay'),
    url(r'^del_switch_bay/(?P<switchbayid>[0-9]+)$',
        views.del_switch_bay,
        name='del-switch-bay'),
    url(r'^index_port_profile/$',
        views.index_port_profile,
        name='index-port-profile'),
    url(r'^new_port_profile/$',
        views.new_port_profile,
        name='new-port-profile'),
    url(r'^edit_port_profile/(?P<portprofileid>[0-9]+)$',
        views.edit_port_profile,
        name='edit-port-profile'),
    url(r'^del_port_profile/(?P<portprofileid>[0-9]+)$',
        views.del_port_profile,
        name='del-port-profile'),
    url(r'^add_module/$', views.add_module, name='add-module'),
    url(r'^edit_module/(?P<moduleswitchid>[0-9]+)$',
        views.edit_module,
        name='edit-module'),
    url(r'^del_module/(?P<moduleswitchid>[0-9]+)$', views.del_module, name='del-module'),
    url(r'^index_module/$', views.index_module, name='index-module'),
    url(r'^add_module_on/$', views.add_module_on, name='add-module-on'),
    url(r'^edit_module_on/(?P<moduleonswitchid>[0-9]+)$',
        views.edit_module_on,
        name='edit-module-on'),
    url(r'^del_module_on/(?P<moduleonswitchid>[0-9]+)$', views.del_module_on, name='del-module-on'),
]
