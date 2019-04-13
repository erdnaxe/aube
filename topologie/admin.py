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
    Building,
    Dormitory,
    Room,
)


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


@admin.register(Room)
class RoomAdmin(VersionAdmin):
    """Register Room object in admin"""
    list_display = ('name', 'building', 'details')
    list_filter = ('building', 'building__dormitory')
    search_fields = ('name', 'building__name', 'building__dormitory__name',
                     'details')
