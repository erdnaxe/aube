# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0007_auto_20160703_1816'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interface',
            name='ipv6',
        ),
    ]
