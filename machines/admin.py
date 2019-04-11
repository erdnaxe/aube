# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""machines.admin
The objects, fields and datastructures visible in the Django admin view
"""

from __future__ import unicode_literals

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import (
    Extension,
    SOA,
    Mx,
    Ns,
    Vlan,
    Txt,
    DName,
    Srv,
    SshFp,
    Nas,
    Service,
    Role,
    OuverturePort,
    Ipv6List,
    OuverturePortList,
)
from .models import IpType, Machine, MachineType, Domain, IpList, Interface


class MachineAdmin(VersionAdmin):
    """ Admin view of a Machine object """
    pass


class Ipv6ListAdmin(VersionAdmin):
    """ Admin view of a Ipv6List object """
    pass


class IpTypeAdmin(VersionAdmin):
    """ Admin view of a IpType object """
    pass


@admin.register(MachineType)
class MachineTypeAdmin(VersionAdmin):
    """Admin view of a MachineType object"""
    list_display = ('name', 'ip_type')


class VlanAdmin(VersionAdmin):
    """ Admin view of a Vlan object """
    pass


class ExtensionAdmin(VersionAdmin):
    """ Admin view of a Extension object """
    pass


class SOAAdmin(VersionAdmin):
    """ Admin view of a SOA object """
    pass


class MxAdmin(VersionAdmin):
    """ Admin view of a MX object """
    pass


class NsAdmin(VersionAdmin):
    """ Admin view of a NS object """
    pass


class TxtAdmin(VersionAdmin):
    """ Admin view of a TXT object """
    pass


class DNameAdmin(VersionAdmin):
    """ Admin view of a DName object """
    pass


class SrvAdmin(VersionAdmin):
    """ Admin view of a SRV object """
    pass


class SshFpAdmin(VersionAdmin):
    """ Admin view of a SSHFP object """
    pass


@admin.register(Nas)
class NasAdmin(VersionAdmin):
    """Admin view of a Nas object"""
    list_display = ('name', 'nas_type', 'machine_type', 'port_access_mode',
                    'autocapture_mac')
    list_filter = ('port_access_mode', 'autocapture_mac', 'nas_type',
                   'machine_type')
    search_fields = ('name',)


class IpListAdmin(VersionAdmin):
    """ Admin view of a Ipv4List object """
    pass


class OuverturePortAdmin(VersionAdmin):
    """ Admin view of a OuverturePort object """
    pass


class OuverturePortListAdmin(VersionAdmin):
    """ Admin view of a OuverturePortList object """
    pass


class InterfaceAdmin(VersionAdmin):
    """ Admin view of a Interface object """
    list_display = ('machine', 'machine_type', 'mac_address', 'ipv4', 'details')


class DomainAdmin(VersionAdmin):
    """ Admin view of a Domain object """
    list_display = ('interface_parent', 'name', 'extension', 'cname')


class ServiceAdmin(VersionAdmin):
    """ Admin view of a ServiceAdmin object """
    list_display = ('service_type', 'min_time_regen', 'regular_time_regen')


class RoleAdmin(VersionAdmin):
    """ Admin view of a RoleAdmin object """
    pass


admin.site.register(Machine, MachineAdmin)
admin.site.register(IpType, IpTypeAdmin)
admin.site.register(Extension, ExtensionAdmin)
admin.site.register(SOA, SOAAdmin)
admin.site.register(Mx, MxAdmin)
admin.site.register(Ns, NsAdmin)
admin.site.register(Txt, TxtAdmin)
admin.site.register(DName, DNameAdmin)
admin.site.register(Srv, SrvAdmin)
admin.site.register(SshFp, SshFpAdmin)
admin.site.register(IpList, IpListAdmin)
admin.site.register(Interface, InterfaceAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Vlan, VlanAdmin)
admin.site.register(Ipv6List, Ipv6ListAdmin)
admin.site.register(OuverturePort, OuverturePortAdmin)
admin.site.register(OuverturePortList, OuverturePortListAdmin)
