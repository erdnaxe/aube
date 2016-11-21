# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0039_auto_20161119_0033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ldapserviceuser',
            name='dn',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='ldapuser',
            name='dn',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='ldapusergroup',
            name='dn',
            field=models.CharField(max_length=200),
        ),
    ]