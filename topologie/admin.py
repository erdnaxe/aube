# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""
Fichier définissant les administration des models dans l'interface admin
"""

from __future__ import unicode_literals

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


class RoomAdmin(VersionAdmin):
    """Administration d'un chambre"""
    pass


class ModelSwitchAdmin(VersionAdmin):
    """Administration d'un modèle de switch"""
    pass


class ConstructorSwitchAdmin(VersionAdmin):
    """Administration d'un constructeur d'un switch"""
    pass


class SwitchBayAdmin(VersionAdmin):
    """Administration d'une baie de brassage"""
    pass


class BuildingAdmin(VersionAdmin):
    """Administration d'un batiment"""
    pass


class DormitoryAdmin(VersionAdmin):
    """Administration d'une residence"""
    pass


class PortProfileAdmin(VersionAdmin):
    """Administration of a port profile"""
    pass

admin.site.register(Port, PortAdmin)
admin.site.register(AccessPoint, AccessPointAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Switch, SwitchAdmin)
admin.site.register(Stack, StackAdmin)
admin.site.register(ModelSwitch, ModelSwitchAdmin)
admin.site.register(ConstructorSwitch, ConstructorSwitchAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Dormitory, DormitoryAdmin)
admin.site.register(SwitchBay, SwitchBayAdmin)
admin.site.register(PortProfile, PortProfileAdmin)
