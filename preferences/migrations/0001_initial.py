# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-25 02:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_display_page', models.IntegerField(default=15)),
            ],
        ),
        migrations.CreateModel(
            name='OptionalMachine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password_machine', models.BooleanField(default=True)),
                ('max_lambdauser_interfaces', models.IntegerField(default=10)),
                ('max_lambdauser_aliases', models.IntegerField(default=10)),
            ],
        ),
        migrations.CreateModel(
            name='OptionalUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_tel_mandatory', models.BooleanField(default=True)),
                ('user_solde', models.BooleanField(default=True)),
            ],
        ),
    ]