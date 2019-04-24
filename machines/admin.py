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
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin

from .models import (
    DName,
    Domain,
    Extension,
    Interface,
    IpType,
    Ipv6List,
    Machine,
    MachineType,
    Mx,
    Nas,
    Ns,
    OuverturePort,
    OuverturePortList,
    Role,
    Service,
    Service_link,
    SOA,
    Srv,
    SshFp,
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
    # TODO(erdnaxe): block range edit after creation


class DomainInline(admin.TabularInline):
    """A inline for Interface, represents one domain"""
    model = Domain
    extra = 1


class Ipv6ListInline(admin.TabularInline):
    """A inline for Interface, represents one ipv6"""
    model = Ipv6List
    extra = 1


@admin.register(Interface)
class InterfaceAdmin(VersionAdmin):
    """Admin view of a Interface object"""
    list_display = ('domain', 'machine', 'machine_type', 'mac_address', 'ipv4')
    list_filter = ('port_lists',)
    inlines = (DomainInline, Ipv6ListInline)
    filter_horizontal = ('port_lists',)
    search_fields = ('domain__name', 'mac_address', 'ipv4__ipv4',
                     'machine__name', 'machine__user__username',
                     'machine__user__surname')
    # TODO(erdnaxe): we need to split alias and domain


class InterfaceInline(admin.StackedInline):
    """A inline for Machine, represents one interface"""
    model = Interface
    filter_horizontal = ('port_lists',)
    extra = 1


class SshFpInline(admin.TabularInline):
    """A inline for Machine, represents one SSH FingerPrint"""
    model = SshFp
    extra = 1


@admin.register(Machine)
class MachineAdmin(VersionAdmin):
    """Admin view of a Machine object"""
    list_display = ('name', 'user', 'active')
    list_filter = ('active',)
    inlines = (InterfaceInline, SshFpInline)
    empty_value_display = _('- no name -')
    search_fields = ('name', 'user__username', 'user__surname')


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


class OuverturePortInline(admin.TabularInline):
    """A inline for OuverturePortListAdmin, represents one range of ports"""
    model = OuverturePort
    extra = 1


@admin.register(OuverturePortList)
class OuverturePortListAdmin(VersionAdmin):
    """Admin view of a OuverturePortList object"""
    list_display = ('name', 'open_ports')
    inlines = (OuverturePortInline,)

    @staticmethod
    def open_ports(obj):
        """All ports refering to a profile"""
        return ", ".join(
            port.show_port() for port in obj.ouvertureport_set.all())

    open_ports.short_description = "open ports"


@admin.register(Role)
class RoleAdmin(VersionAdmin):
    """Admin view of a Role object"""
    list_display = ('role_type', 'specific_role')
    filter_horizontal = ('servers',)
    # TODO(erdnaxe): investigate why it was buggy before switching to admin
    # TODO(erdnaxe): print machines on change list like in edit mode


@admin.register(Srv)
class SrvAdmin(VersionAdmin):
    """Admin view of a Srv object"""
    list_display = ('service', 'protocole', 'extension', 'ttl', 'priority',
                    'weight', 'port', 'target')


class ServiceLinkInline(admin.TabularInline):
    """A inline for ServiceAdmin, represents one association"""
    model = Service_link
    extra = 1


@admin.register(Service)
class ServiceAdmin(VersionAdmin):
    """Admin view of a Service object"""
    list_display = ('service_type', 'min_time_regen', 'regular_time_regen')
    inlines = (ServiceLinkInline,)
    # TODO(erdnaxe): print machines on change list like in edit mode


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
