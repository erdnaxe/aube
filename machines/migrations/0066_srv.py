# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-16 00:10
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0065_auto_20171115_1514'),
    ]

    operations = [
        migrations.CreateModel(
            name='Srv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(max_length=31)),
                ('protocole', models.CharField(choices=[('TCP', 'TCP'), ('UDP', 'UDP')], default='TCP', max_length=3)),
                ('ttl', models.PositiveIntegerField(default=172800, help_text='Time To Live')),
                ('priority', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(65535)])),
                ('weight', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(65535)])),
                ('port', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(65535)])),
                ('extension', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='machines.Extension')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='machines.Domain')),
            ],
        ),
    ]