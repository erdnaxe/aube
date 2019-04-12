# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2019  Alexandre Iooss
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""machines.admin
The objects, fields and datastructures visible in the Django admin view
"""

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import (
    Extension,
    DName,
    MachineType,
    Mx,
    Nas,
    Ns,
    SOA,
    Srv,
    Txt,
    Vlan,
)


@admin.register(Extension)
class ExtensionAdmin(VersionAdmin):
    """Admin view of a Extension object"""
    list_display = ('name', 'need_infra', 'origin', 'soa', 'dnssec')


@admin.register(DName)
class DNameAdmin(VersionAdmin):
    """Admin view of a DName object"""
    list_display = ('zone', 'alias')


@admin.register(MachineType)
class MachineTypeAdmin(VersionAdmin):
    """Admin view of a MachineType object"""
    list_display = ('name', 'ip_type')


@admin.register(Mx)
class MxAdmin(VersionAdmin):
    """Admin view of a Mx object"""
    list_display = ('zone', 'priority', 'name')


@admin.register(Nas)
class NasAdmin(VersionAdmin):
    """Admin view of a Nas object"""
    list_display = ('nas_type', 'machine_type', 'port_access_mode',
                    'autocapture_mac')
    list_filter = ('port_access_mode', 'autocapture_mac')


@admin.register(Ns)
class NsAdmin(VersionAdmin):
    """Admin view of a Ns object"""
    list_display = ('zone', 'ns')


@admin.register(Srv)
class SrvAdmin(VersionAdmin):
    """Admin view of a Srv object"""
    list_display = ('service', 'protocole', 'extension', 'ttl', 'priority',
                    'weight', 'port', 'target')


@admin.register(SOA)
class SOAAdmin(VersionAdmin):
    """Admin view of a SOA object"""
    list_display = ('name', 'mail', 'refresh', 'retry', 'expire', 'ttl')


@admin.register(Txt)
class TxtAdmin(VersionAdmin):
    """Admin view of a Txt object"""
    list_display = ('zone', 'field1', 'field2')


@admin.register(Vlan)
class VlanAdmin(VersionAdmin):
    """Admin view of a VLAN object"""
    list_display = ('vlan_id', 'name', 'comment')
    list_filter = ('dhcp_snooping', 'dhcpv6_snooping', 'igmp', 'mld')
