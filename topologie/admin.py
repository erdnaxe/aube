# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2019  Alexandre Iooss
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""Defines models in admin interface"""

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import (
    Port,
    Room,
    Switch,
    Stack,
    ModelSwitch,
    ConstructorSwitch,
    AccessPoint,
    SwitchBay,
    Building,
    Dormitory,
    PortProfile,
)


class StackAdmin(VersionAdmin):
    """Administration d'une stack de switches (inclus des switches)"""
    pass


class SwitchAdmin(VersionAdmin):
    """Administration d'un switch"""
    pass


class PortAdmin(VersionAdmin):
    """Administration d'un port de switches"""
    pass


class AccessPointAdmin(VersionAdmin):
    """Administration d'une borne"""
    pass


@admin.register(Room)
class RoomAdmin(VersionAdmin):
    """Register Room object in admin"""
    list_display = ('name', 'building', 'details')
    list_filter = ('building', 'building__dormitory')
    search_fields = ('name', 'building__name', 'building__dormitory__name',
                     'details')


class ModelSwitchAdmin(VersionAdmin):
    """Administration d'un modèle de switch"""
    pass


class ConstructorSwitchAdmin(VersionAdmin):
    """Administration d'un constructeur d'un switch"""
    pass


class SwitchBayAdmin(VersionAdmin):
    """Administration d'une baie de brassage"""
    pass


@admin.register(Building)
class BuildingAdmin(VersionAdmin):
    """Register Dormitory object in admin"""
    list_display = ('name', 'dormitory')
    search_fields = ('name', 'dormitory__name')
    list_filter = ('dormitory',)


@admin.register(Dormitory)
class DormitoryAdmin(VersionAdmin):
    """Register Dormitory object in admin"""
    list_display = ('name',)
    search_fields = ('name',)


class PortProfileAdmin(VersionAdmin):
    """Administration of a port profile"""
    pass


admin.site.register(Port, PortAdmin)
admin.site.register(AccessPoint, AccessPointAdmin)
admin.site.register(Switch, SwitchAdmin)
admin.site.register(Stack, StackAdmin)
admin.site.register(ModelSwitch, ModelSwitchAdmin)
admin.site.register(ConstructorSwitch, ConstructorSwitchAdmin)
admin.site.register(SwitchBay, SwitchBayAdmin)
admin.site.register(PortProfile, PortProfileAdmin)
