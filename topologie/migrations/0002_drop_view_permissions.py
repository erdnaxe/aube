# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-04-08 17:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0001_initial_from_re2o'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['building__name'], 'verbose_name': 'room', 'verbose_name_plural': 'rooms'},
        ),
        migrations.AlterModelOptions(
            name='accesspoint',
            options={'verbose_name': 'access point', 'verbose_name_plural': 'access points'},
        ),
        migrations.AlterModelOptions(
            name='building',
            options={'verbose_name': 'building', 'verbose_name_plural': 'buildings'},
        ),
        migrations.AlterModelOptions(
            name='constructorswitch',
            options={'verbose_name': 'switch constructor', 'verbose_name_plural': 'switch constructors'},
        ),
        migrations.AlterModelOptions(
            name='dormitory',
            options={'verbose_name': 'dormitory', 'verbose_name_plural': 'dormitories'},
        ),
        migrations.AlterModelOptions(
            name='modelswitch',
            options={'verbose_name': 'switch model', 'verbose_name_plural': 'switch models'},
        ),
        migrations.AlterModelOptions(
            name='moduleonswitch',
            options={'verbose_name': 'link between switch and module', 'verbose_name_plural': 'links between switch and module'},
        ),
        migrations.AlterModelOptions(
            name='moduleswitch',
            options={'verbose_name': 'switch module', 'verbose_name_plural': 'switch modules'},
        ),
        migrations.AlterModelOptions(
            name='port',
            options={'verbose_name': 'port', 'verbose_name_plural': 'ports'},
        ),
        migrations.AlterModelOptions(
            name='portprofile',
            options={'verbose_name': 'port profile', 'verbose_name_plural': 'port profiles'},
        ),
        migrations.AlterModelOptions(
            name='stack',
            options={'verbose_name': 'switches stack', 'verbose_name_plural': 'switches stacks'},
        ),
        migrations.AlterModelOptions(
            name='switch',
            options={'verbose_name': 'switch', 'verbose_name_plural': 'switches'},
        ),
        migrations.AlterModelOptions(
            name='switchbay',
            options={'verbose_name': 'switch bay', 'verbose_name_plural': 'switch bays'},
        ),
    ]
