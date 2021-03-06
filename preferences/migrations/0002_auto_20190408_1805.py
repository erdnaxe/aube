# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-04-08 16:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import preferences.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial_from_re2o'),
        ('machines', '0002_auto_20190408_1805'),
        ('preferences', '0001_initial_from_re2o'),
        ('reversion', '0001_squashed_0004_auto_20160611_1202'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='optionaluser',
            name='shell_default',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.ListShell'),
        ),
        migrations.AddField(
            model_name='optionaltopologie',
            name='switchs_ip_type',
            field=models.OneToOneField(blank=True, help_text='IP range for the management of switches', null=True, on_delete=django.db.models.deletion.PROTECT, to='machines.IpType'),
        ),
        migrations.AddField(
            model_name='cotisationsoption',
            name='invoice_template',
            field=models.OneToOneField(default=preferences.models.default_invoice, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_template', to='preferences.DocumentTemplate', verbose_name='Template for invoices'),
        ),
        migrations.AddField(
            model_name='cotisationsoption',
            name='voucher_template',
            field=models.OneToOneField(default=preferences.models.default_voucher, on_delete=django.db.models.deletion.PROTECT, related_name='voucher_template', to='preferences.DocumentTemplate', verbose_name='Template for subscription voucher'),
        ),
        migrations.AddField(
            model_name='assooption',
            name='utilisateur_asso',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
