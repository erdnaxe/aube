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
    DName,
    Extension,
    IpType,
    MachineType,
    Mx,
    Nas,
    Ns,
    OuverturePort,
    OuverturePortList,
    Role,
    SOA,
    Srv,
    Txt,
    Vlan,
)


@admin.register(DName)
class DNameAdmin(VersionAdmin):
    """Admin view of a DName object"""
    list_display = ('zone', 'alias')


@admin.register(Extension)
class ExtensionAdmin(VersionAdmin):
    """Admin view of a Extension object"""
    list_display = ('name', 'need_infra', 'origin', 'soa', 'dnssec')


@admin.register(IpType)
class IpTypeAdmin(VersionAdmin):
    """Admin view of a IpType object"""
    list_display = (
        'name', 'extension', 'need_infra', 'prefix_v6', 'vlan',
        'ouverture_ports')
    list_filter = ('need_infra',)


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


class OuverturePortInline(admin.TabularInline):
    """A inline for OuverturePortListAdmin, represents one range of ports"""
    model = OuverturePort
    extra = 1


@admin.register(OuverturePortList)
class OuverturePortListAdmin(VersionAdmin):
    """Admin view of a OuverturePortList object"""
    list_display = ('name', 'tcp_in', 'tcp_out', 'udp_in', 'udp_out')
    inlines = (OuverturePortInline,)

    # TODO(erdnaxe): add machines list

    def tcp_in(self, obj):
        return None

    def tcp_out(self, obj):
        return None

    def udp_in(self, obj):
        return None

    def udp_out(self, obj):
        return None


@admin.register(Role)
class RoleAdmin(VersionAdmin):
    """Admin view of a Role object"""
    list_display = ('role_type', 'specific_role', 'servers')
    # TODO(erdnaxe): investigate why it was buggy before switching to admin
    # TODO(erdnaxe): print machines on change list like in edit mode
    #     role_list = (Role.objects
    #                  .prefetch_related(
    #         'servers__domain__extension'
    #     ).all())


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
