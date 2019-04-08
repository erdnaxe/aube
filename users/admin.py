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
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from reversion.admin import VersionAdmin

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
    LdapUser,
    LdapServiceUser,
    LdapServiceUserGroup,
    LdapUserGroup
)
from .forms import (
    UserChangeForm,
    UserCreationForm,
    ServiceUserChangeForm,
    ServiceUserCreationForm
)


class LdapUserAdmin(admin.ModelAdmin):
    """Administration du ldapuser"""
    list_display = ('name', 'uidNumber', 'login_shell')
    exclude = ('user_password', 'sambat_nt_password')
    search_fields = ('name',)


class LdapServiceUserAdmin(admin.ModelAdmin):
    """Administration du ldapserviceuser"""
    list_display = ('name',)
    exclude = ('user_password',)
    search_fields = ('name',)


class LdapUserGroupAdmin(admin.ModelAdmin):
    """Administration du ldapusergroupe"""
    list_display = ('name', 'members', 'gid')
    search_fields = ('name',)


class LdapServiceUserGroupAdmin(admin.ModelAdmin):
    """Administration du ldap serviceusergroup"""
    list_display = ('name',)
    search_fields = ('name',)


class SchoolAdmin(VersionAdmin):
    """Administration, gestion des écoles"""
    pass


class ListRightAdmin(VersionAdmin):
    """Gestion de la liste des droits existants
    Ne permet pas l'edition du gid (primarykey pour ldap)"""
    list_display = ('unix_name',)


class ListShellAdmin(VersionAdmin):
    """Gestion de la liste des shells coté admin"""
    pass


class RequestAdmin(admin.ModelAdmin):
    """Gestion des request objet, ticket pour lien de reinit mot de passe"""
    list_display = ('user', 'type', 'created_at', 'expires_at')


class BanAdmin(VersionAdmin):
    """Gestion des bannissements"""
    pass


class EMailAddressAdmin(VersionAdmin):
    """Gestion des alias mail"""
    pass


class WhitelistAdmin(VersionAdmin):
    """Gestion des whitelist"""
    pass


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
        ('Permissions', {'fields': ('is_admin', )}),
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
admin.site.register(LdapUser, LdapUserAdmin)
admin.site.register(LdapUserGroup, LdapUserGroupAdmin)
admin.site.register(LdapServiceUser, LdapServiceUserAdmin)
admin.site.register(LdapServiceUserGroup, LdapServiceUserGroupAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(ListRight, ListRightAdmin)
admin.site.register(ListShell, ListShellAdmin)
admin.site.register(Ban, BanAdmin)
admin.site.register(EMailAddress, EMailAddressAdmin)
admin.site.register(Whitelist, WhitelistAdmin)
admin.site.register(Request, RequestAdmin)
# Now register the new UserAdmin...
admin.site.unregister(User)
admin.site.unregister(ServiceUser)
admin.site.register(User, UserAdmin)
admin.site.register(ServiceUser, ServiceUserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
