# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-25 21:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0010_auto_20170825_0459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='optionaltopologie',
            name='vlan_decision_nok',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='decision_nok', to='machines.Vlan'),
        ),
        migrations.AlterField(
            model_name='optionaltopologie',
            name='vlan_decision_ok',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='decision_ok', to='machines.Vlan'),
        ),
        migrations.DeleteModel(
            name='Vlan',
        ),
    ]