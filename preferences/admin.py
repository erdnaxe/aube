# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""
Classes admin pour les models de preferences
"""
from __future__ import unicode_literals

from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import (
    OptionalUser,
    OptionalMachine,
    OptionalTopologie,
    GeneralOption,
    Service,
    MailContact,
    AssoOption,
    MailMessageOption,
    HomeOption,
    RadiusKey,
    SwitchManagementCred,
    Reminder,
    DocumentTemplate
)


class OptionalUserAdmin(VersionAdmin):
    """Class admin options user"""
    pass


class OptionalTopologieAdmin(VersionAdmin):
    """Class admin options topologie"""
    pass


class OptionalMachineAdmin(VersionAdmin):
    """Class admin options machines"""
    pass


class GeneralOptionAdmin(VersionAdmin):
    """Class admin options générales"""
    pass


class ServiceAdmin(VersionAdmin):
    """Class admin gestion des services de la page d'accueil"""
    pass


class MailContactAdmin(VersionAdmin):
    """Admin class for contact email adresses"""
    pass


class AssoOptionAdmin(VersionAdmin):
    """Class admin options de l'asso"""
    pass


class MailMessageOptionAdmin(VersionAdmin):
    """Class admin options mail"""
    pass


class HomeOptionAdmin(VersionAdmin):
    """Class admin options home"""
    pass


class RadiusKeyAdmin(VersionAdmin):
    """Class radiuskey"""
    pass

class SwitchManagementCredAdmin(VersionAdmin):
    """Class managementcred for switch"""
    pass

class ReminderAdmin(VersionAdmin):
    """Class reminder for switch"""
    pass


class DocumentTemplateAdmin(VersionAdmin):
    """Admin class for DocumentTemplate"""
    pass


admin.site.register(OptionalUser, OptionalUserAdmin)
admin.site.register(OptionalMachine, OptionalMachineAdmin)
admin.site.register(OptionalTopologie, OptionalTopologieAdmin)
admin.site.register(GeneralOption, GeneralOptionAdmin)
admin.site.register(HomeOption, HomeOptionAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(MailContact, MailContactAdmin)
admin.site.register(Reminder, ReminderAdmin)
admin.site.register(RadiusKey, RadiusKeyAdmin)
admin.site.register(SwitchManagementCred, SwitchManagementCredAdmin)
admin.site.register(AssoOption, AssoOptionAdmin)
admin.site.register(MailMessageOption, MailMessageOptionAdmin)
admin.site.register(DocumentTemplate, DocumentTemplateAdmin)
