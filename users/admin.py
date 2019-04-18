# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""
Definition des vues pour les admin. Classique, sauf pour users,
où on fait appel à UserChange et ServiceUserChange, forms custom
"""

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from reversion.admin import VersionAdmin

from .forms import (
    UserChangeForm,
    UserCreationForm,
    ServiceUserChangeForm,
    ServiceUserCreationForm
)
from .models import (
    User,
    EMailAddress,
    ServiceUser,
    School,
    ListRight,
    ListShell,
    Adherent,
    Club,
    Ban,
    Whitelist,
    Request,
)


@admin.register(School)
class SchoolAdmin(VersionAdmin):
    """Manage all schools in admin"""
    list_display = ('name',)
    search_fields = ('name',)


class ListRightAdmin(VersionAdmin):
    """Gestion de la liste des droits existants
    Ne permet pas l'edition du gid (primarykey pour ldap)"""
    list_display = ('unix_name',)


@admin.register(ListShell)
class ListShellAdmin(VersionAdmin):
    """Manage available shells in admin"""
    list_display = ('shell',)
    search_fields = ('shell',)


class RequestAdmin(admin.ModelAdmin):
    """Gestion des request objet, ticket pour lien de reinit mot de passe"""
    list_display = ('user', 'type', 'created_at', 'expires_at')


@admin.register(Ban)
class BanAdmin(VersionAdmin):
    """Manage blacklist in admin"""
    list_display = ('user', 'state', 'raison', 'date_start', 'date_end')
    list_filter = ('state', 'date_start', 'date_end')


class EMailAddressAdmin(VersionAdmin):
    """Gestion des alias mail"""
    pass


@admin.register(Whitelist)
class WhitelistAdmin(VersionAdmin):
    """Manage whitelist in admin"""
    list_display = ('user', 'raison', 'date_start', 'date_end')
    list_filter = ('date_start', 'date_end')


class UserAdmin(VersionAdmin, BaseUserAdmin):
    """Gestion d'un user : modification des champs perso, mot de passe, etc"""
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = (
        'pseudo',
        'surname',
        'email',
        'local_email_redirect',
        'local_email_enabled',
        'school',
        'is_admin',
        'shell'
    )
    # Need to reset the settings from BaseUserAdmin
    # They are using fields we don't use like 'is_staff'
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('pseudo', 'password')}),
        (
            'Personal info',
            {
                'fields':
                    ('surname', 'email', 'school', 'shell', 'uid_number')
            }
        ),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'pseudo',
                    'surname',
                    'email',
                    'school',
                    'is_admin',
                    'password1',
                    'password2'
                )
            }
        ),
    )
    search_fields = ('pseudo', 'surname')
    ordering = ('pseudo',)
    filter_horizontal = ()


class ServiceUserAdmin(VersionAdmin, BaseUserAdmin):
    """Gestion d'un service user admin : champs personnels,
    mot de passe; etc"""
    # The forms to add and change user instances
    form = ServiceUserChangeForm
    add_form = ServiceUserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('pseudo', 'access_group')
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('pseudo', 'password', 'access_group')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('pseudo', 'password1', 'password2')
            }
        ),
    )
    search_fields = ('pseudo',)
    ordering = ('pseudo',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(Adherent, UserAdmin)
admin.site.register(Club, UserAdmin)
admin.site.register(ServiceUser, ServiceUserAdmin)
admin.site.register(ListRight, ListRightAdmin)
admin.site.register(EMailAddress, EMailAddressAdmin)
admin.site.register(Request, RequestAdmin)
# Now register the new UserAdmin...
admin.site.unregister(User)
admin.site.unregister(ServiceUser)
admin.site.register(User, UserAdmin)
admin.site.register(ServiceUser, ServiceUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
