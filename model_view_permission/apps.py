# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: BSD 2-Clause "Simplified" License
#
# Copyright © 2019  Alexandre Iooss
# Copyright © 2016  Context Information Security

"""
This entire app will need to be dropped when upgrading to Django 2.2
Loosely based on https://github.com/ctxis/django-admin-view-permission
"""

from django.apps import AppConfig
from django.apps import apps as global_apps
from django.contrib import admin
from django.db.models.signals import post_migrate

from .admin import ModelViewPermissionAdminSite


def update_permissions(sender, apps=global_apps, **kwargs):
    """Add view permission to all models, like in Django 2.1"""
    for app in apps.get_app_configs():
        for model in app.get_models():
            view_permission = 'view_%s' % model._meta.model_name
            if view_permission not in [perm[0] for perm in
                                       model._meta.permissions]:
                model._meta.permissions += (
                    ('view_%s' % model._meta.model_name,
                     'Can view %s' % model._meta.model_name),
                )


class ModelViewPermissionConfig(AppConfig):
    name = 'model_view_permission'

    def ready(self):
        """Override Django init to load update_permissions and admin site"""
        # By default use ModelViewPermissionAdminSite admin site
        if not isinstance(admin.site, ModelViewPermissionAdminSite):
            admin.site = ModelViewPermissionAdminSite('admin')
            admin.sites.site = admin.site

        # Add permission
        post_migrate.connect(update_permissions)
