# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-08-18 11:21
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0075_merge_20180815_2202'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adherent',
            options={'verbose_name': 'member', 'verbose_name_plural': 'members'},
        ),
        migrations.AlterModelOptions(
            name='ban',
            options={'permissions': (('view_ban', 'Can view a ban object'),), 'verbose_name': 'ban', 'verbose_name_plural': 'bans'},
        ),
        migrations.AlterModelOptions(
            name='club',
            options={'verbose_name': 'club', 'verbose_name_plural': 'clubs'},
        ),
        migrations.AlterModelOptions(
            name='emailaddress',
            options={'permissions': (('view_emailaddress', 'Can view a local email account object'),), 'verbose_name': 'local email account', 'verbose_name_plural': 'local email accounts'},
        ),
        migrations.AlterModelOptions(
            name='listright',
            options={'permissions': (('view_listright', 'Can view a group of rights object'),), 'verbose_name': 'group of rights', 'verbose_name_plural': 'groups of rights'},
        ),
        migrations.AlterModelOptions(
            name='listshell',
            options={'permissions': (('view_listshell', 'Can view a shell object'),), 'verbose_name': 'shell', 'verbose_name_plural': 'shells'},
        ),
        migrations.AlterModelOptions(
            name='school',
            options={'permissions': (('view_school', 'Can view a school object'),), 'verbose_name': 'school', 'verbose_name_plural': 'schools'},
        ),
        migrations.AlterModelOptions(
            name='serviceuser',
            options={'permissions': (('view_serviceuser', 'Can view a service user object'),), 'verbose_name': 'service user', 'verbose_name_plural': 'service users'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (('change_user_password', 'Can change the password of a user'), ('change_user_state', 'Can edit the state of a user'), ('change_user_force', 'Can force the move'), ('change_user_shell', 'Can edit the shell of a user'), ('change_user_groups', 'Can edit the groups of rights of a user (critical permission)'), ('change_all_users', 'Can edit all users, including those with rights.'), ('view_user', 'Can view a user object')), 'verbose_name': 'user (member or club)', 'verbose_name_plural': 'users (members or clubs)'},
        ),
        migrations.AlterModelOptions(
            name='whitelist',
            options={'permissions': (('view_whitelist', 'Can view a whitelist object'),), 'verbose_name': 'whitelist (free of charge access)', 'verbose_name_plural': 'whitelists (free of charge access)'},
        ),
        migrations.AlterField(
            model_name='adherent',
            name='gpg_fingerprint',
            field=models.CharField(blank=True, max_length=40, null=True, validators=[django.core.validators.RegexValidator('^[0-9A-F]{40}$', message='A GPG fingerprint must contain 40 hexadecimal characters.')]),
        ),
        migrations.AlterField(
            model_name='ban',
            name='state',
            field=models.IntegerField(choices=[(0, 'HARD (no access)'), (1, 'SOFT (local access only)'), (2, 'RESTRICTED (speed limitation)')], default=0),
        ),
        migrations.AlterField(
            model_name='emailaddress',
            name='user',
            field=models.ForeignKey(help_text='User of the local email account', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='listright',
            name='unix_name',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator('^[a-z]+$', message='UNIX groups can only contain lower case letters.')]),
        ),
        migrations.AlterField(
            model_name='request',
            name='type',
            field=models.CharField(choices=[('PW', 'Password'), ('EM', 'Email address')], max_length=2),
        ),
        migrations.AlterField(
            model_name='serviceuser',
            name='comment',
            field=models.CharField(blank=True, help_text='Comment', max_length=255),
        ),
        migrations.AlterField(
            model_name='serviceuser',
            name='pseudo',
            field=models.CharField(help_text='Must only contain letters, numerals or dashes.', max_length=32, unique=True, validators=[users.models.linux_user_validator]),
        ),
        migrations.AlterField(
            model_name='user',
            name='comment',
            field=models.CharField(blank=True, help_text='Comment, school year', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='local_email_redirect',
            field=models.BooleanField(default=False, help_text='Enable redirection of the local email messages to the main email address.'),
        ),
        migrations.AlterField(
            model_name='user',
            name='pseudo',
            field=models.CharField(help_text='Must only contain letters, numerals or dashes.', max_length=32, unique=True, validators=[users.models.linux_user_validator]),
        ),
    ]
