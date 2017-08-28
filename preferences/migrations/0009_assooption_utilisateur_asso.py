# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-24 19:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('preferences', '0008_auto_20170824_2122'),
    ]

    operations = [
        migrations.AddField(
            model_name='assooption',
            name='utilisateur_asso',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]