# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-08-14 08:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0073_auto_20180629_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, null=True, help_text='External email address allowing us to contact you.', max_length=254),
        ),
        migrations.AlterField(
            model_name='user',
            name='local_email_enabled',
            field=models.BooleanField(default=False, help_text='Enable the local email account.'),
        ),
        migrations.AlterField(
            model_name='user',
            name='local_email_redirect',
            field=models.BooleanField(default=False, help_text='Enable redirection of the local email messages to the main email.'),
        ),
    ]
