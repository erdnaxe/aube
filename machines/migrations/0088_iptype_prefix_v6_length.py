# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-07-16 18:46
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0087_dnssec'),
    ]

    operations = [
        migrations.AddField(
            model_name='iptype',
            name='prefix_v6_length',
            field=models.IntegerField(default=64, validators=[django.core.validators.MaxValueValidator(128), django.core.validators.MinValueValidator(0)]),
        ),
    ]
