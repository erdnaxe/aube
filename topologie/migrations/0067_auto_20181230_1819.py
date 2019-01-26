# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-12-30 17:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import re2o.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0066_modelswitch_commercial_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleOnSwitch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.CharField(help_text='Slot on switch', max_length=15, verbose_name='Slot')),
            ],
            options={
                'verbose_name': 'link between switchs and modules',
                'permissions': (('view_moduleonswitch', 'Can view a moduleonswitch object'),),
            },
            bases=(re2o.mixins.AclMixin, re2o.mixins.RevMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ModuleSwitch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(help_text='Reference of a module', max_length=255, verbose_name='Module reference')),
                ('comment', models.CharField(blank=True, help_text='Comment', max_length=255, null=True, verbose_name='Comment')),
            ],
            options={
                'verbose_name': 'Module of a switch',
                'permissions': (('view_moduleswitch', 'Can view a module object'),),
            },
            bases=(re2o.mixins.AclMixin, re2o.mixins.RevMixin, models.Model),
        ),
        migrations.AddField(
            model_name='modelswitch',
            name='is_itself_module',
            field=models.BooleanField(default=False, help_text='Does the switch, itself, considered as a module'),
        ),
        migrations.AddField(
            model_name='modelswitch',
            name='is_modular',
            field=models.BooleanField(default=False, help_text='Is this switch model modular'),
        ),
        migrations.AddField(
            model_name='moduleonswitch',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topologie.ModuleSwitch'),
        ),
        migrations.AddField(
            model_name='moduleonswitch',
            name='switch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topologie.Switch'),
        ),
        migrations.AlterUniqueTogether(
            name='moduleonswitch',
            unique_together=set([('slot', 'switch')]),
        ),
    ]