# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-13 13:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0027_auto_20170905_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='port',
            name='radius',
            field=models.CharField(choices=[('NO', 'NO'), ('STRICT', 'STRICT'), ('BLOQ', 'BLOQ'), ('COMMON', 'COMMON'), ('2', '2'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('20', '20')], default='NO', max_length=32),
        ),
    ]
