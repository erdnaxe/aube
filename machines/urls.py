# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""machines.urls
The defined URLs for the Machines app
"""

from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^new_machine/(?P<userid>[0-9]+)$',
        views.new_machine,
        name='new-machine'),
    url(r'^edit_interface/(?P<interfaceid>[0-9]+)$',
        views.edit_interface,
        name='edit-interface'),
    url(r'^del_machine/(?P<machineid>[0-9]+)$',
        views.del_machine,
        name='del-machine'),
    url(r'^new_interface/(?P<machineid>[0-9]+)$',
        views.new_interface,
        name='new-interface'),
    url(r'^del_interface/(?P<interfaceid>[0-9]+)$',
        views.del_interface,
        name='del-interface'),
    url(r'^index_iptype/$', views.index_iptype, name='index-iptype'),
    url(r'^new_sshfp/(?P<machineid>[0-9]+)$',
        views.new_sshfp,
        name='new-sshfp'),
    url(r'^edit_sshfp/(?P<sshfpid>[0-9]+)$',
        views.edit_sshfp,
        name='edit-sshfp'),
    url(r'^del_sshfp/(?P<sshfpid>[0-9]+)$',
        views.del_sshfp,
        name='del-sshfp'),
    url(r'^index_sshfp/(?P<machineid>[0-9]+)$',
        views.index_sshfp,
        name='index-sshfp'),
    url(r'^add_alias/(?P<interfaceid>[0-9]+)$',
        views.add_alias,
        name='add-alias'),
    url(r'^edit_alias/(?P<domainid>[0-9]+)$',
        views.edit_alias,
        name='edit-alias'),
    url(r'^del_alias/(?P<interfaceid>[0-9]+)$',
        views.del_alias,
        name='del-alias'),
    url(r'^index_alias/(?P<interfaceid>[0-9]+)$',
        views.index_alias,
        name='index-alias'),
    url(r'^new_ipv6list/(?P<interfaceid>[0-9]+)$',
        views.new_ipv6list,
        name='new-ipv6list'),
    url(r'^edit_ipv6list/(?P<ipv6listid>[0-9]+)$',
        views.edit_ipv6list,
        name='edit-ipv6list'),
    url(r'^del_ipv6list/(?P<ipv6listid>[0-9]+)$',
        views.del_ipv6list,
        name='del-ipv6list'),
    url(r'^index_ipv6/(?P<interfaceid>[0-9]+)$',
        views.index_ipv6,
        name='index-ipv6'),
    url(r'^regen_service/(?P<serviceid>[0-9]+)$', views.regen_service, name='regen-service'),
    url(r'^index_service/$', views.index_service, name='index-service'),
    url(r'^$', views.index, name='index'),
    url(r'^rest/mac-ip/$', views.mac_ip, name='mac-ip'),
    url(r'^rest/regen-achieved/$',
        views.regen_achieved,
        name='regen-achieved'),
    url(r'^rest/mac-ip-dns/$', views.mac_ip_dns, name='mac-ip-dns'),
    url(r'^rest/alias/$', views.alias, name='alias'),
    url(r'^rest/corresp/$', views.corresp, name='corresp'),
    url(r'^rest/mx/$', views.mx, name='mx'),
    url(r'^rest/ns/$', views.ns, name='ns'),
    url(r'^rest/txt/$', views.txt, name='txt'),
    url(r'^rest/srv/$', views.srv, name='srv'),
    url(r'^rest/zones/$', views.zones, name='zones'),
    url(r'^rest/service_servers/$',
        views.service_servers,
        name='service-servers'),
    url(r'^rest/ouverture_ports/$',
        views.ouverture_ports,
        name='ouverture-ports'),
    url(r'^port_config/(?P<interfaceid>[0-9]+)$',
        views.configure_ports,
        name='port-config'),
]
