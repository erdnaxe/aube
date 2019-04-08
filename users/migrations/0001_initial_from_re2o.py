# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2019  Alexandre Iooss

from __future__ import unicode_literals

import datetime

import django.core.validators
import django.db.models.deletion
import ldapdb.models.fields
from django.conf import settings
from django.db import migrations, models
from django.utils.timezone import utc

import re2o.mixins
import users.models


def move_passwords(apps, schema_editor):
    User = apps.get_model('users', 'User')
    for row in User.objects.all():
        row.password = row.pwd_ssha
        row.save()


def create_move_room(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Adherent = apps.get_model('users', 'Adherent')
    Club = apps.get_model('users', 'Club')
    db_alias = schema_editor.connection.alias
    users = Adherent.objects.using(db_alias).all()
    clubs = Club.objects.using(db_alias).all()
    for user in users:
        user.room_adherent_id = user.room_id
        user.save(using=db_alias)
    for user in clubs:
        user.room_club_id = user.room_id
        user.save(using=db_alias)


def delete_move_room(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Adherent = apps.get_model('users', 'Adherent')
    Club = apps.get_model('users', 'Club')
    db_alias = schema_editor.connection.alias
    users = Adherent.objects.using(db_alias).all()
    clubs = Club.objects.using(db_alias).all()
    for user in users:
        user.room_id = user.room_adherent_id
        user.save(using=db_alias)
    for user in clubs:
        user.room_id = user.room_club_id
        user.save(using=db_alias)


def create_groups(apps, schema_editor):
    group = apps.get_model("auth", "Group")
    listrights = apps.get_model("users", "ListRight")
    db_alias = schema_editor.connection.alias
    for gr in listrights.objects.using(db_alias).all():
        grp = group()
        grp.name = gr.unix_name
        grp.save()
        gr.group_ptr = grp
        gr.save()


def delete_groups(apps, schema_editor):
    group = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias
    group.objects.using(db_alias).all().delete()


def transfer_right(apps, schema_editor):
    rights = apps.get_model("users", "Right")
    db_alias = schema_editor.connection.alias
    for rg in rights.objects.using(db_alias).all():
        group = rg.right
        u = rg.user
        u.groups.add(group.group_ptr)
        u.save()


def untransfer_right(apps, schema_editor):
    return


def transfer_permissions(apps, schema_editor):
    permission_groups = {'bofh': ['add_ban',
                                  'change_ban',
                                  'delete_ban',
                                  'view_ban',
                                  'add_club',
                                  'change_club',
                                  'delete_club',
                                  'add_user',
                                  'change_user',
                                  'change_user_force',
                                  'change_user_password',
                                  'change_user_shell',
                                  'view_user',
                                  'add_whitelist',
                                  'change_whitelist',
                                  'delete_whitelist',
                                  'view_whitelist'],
                         'bureau': ['add_logentry',
                                    'change_logentry',
                                    'delete_logentry',
                                    'add_group',
                                    'change_group',
                                    'delete_group',
                                    'add_permission',
                                    'change_permission',
                                    'delete_permission',
                                    'add_adherent',
                                    'change_adherent',
                                    'delete_adherent',
                                    'add_ban',
                                    'change_ban',
                                    'delete_ban',
                                    'view_ban',
                                    'add_club',
                                    'change_club',
                                    'delete_club',
                                    'add_listright',
                                    'change_listright',
                                    'delete_listright',
                                    'view_listright',
                                    'add_school',
                                    'change_school',
                                    'delete_school',
                                    'view_school',
                                    'add_user',
                                    'change_user',
                                    'change_user_force',
                                    'change_user_groups',
                                    'change_user_password',
                                    'change_user_shell',
                                    'change_user_state',
                                    'delete_user',
                                    'view_user',
                                    'add_whitelist',
                                    'change_whitelist',
                                    'delete_whitelist',
                                    'view_whitelist'],
                         'cableur': ['add_logentry',
                                     'view_article',
                                     'add_banque',
                                     'change_banque',
                                     'delete_banque',
                                     'view_banque',
                                     'add_cotisation',
                                     'change_cotisation',
                                     'delete_cotisation',
                                     'view_cotisation',
                                     'add_facture',
                                     'can_create',
                                     'can_delete',
                                     'can_edit',
                                     'can_view',
                                     'can_view_all',
                                     'change_facture',
                                     'delete_facture',
                                     'view_facture',
                                     'view_paiement',
                                     'add_vente',
                                     'change_vente',
                                     'delete_vente',
                                     'view_vente',
                                     'add_domain',
                                     'change_domain',
                                     'delete_domain',
                                     'view_domain',
                                     'use_all_extension',
                                     'view_extension',
                                     'add_interface',
                                     'change_interface',
                                     'delete_interface',
                                     'view_interface',
                                     'view_iplist',
                                     'view_iptype',
                                     'add_machine',
                                     'change_machine',
                                     'view_machine',
                                     'view_machinetype',
                                     'view_mx',
                                     'view_nas',
                                     'view_ns',
                                     'view_ouvertureportlist',
                                     'view_service',
                                     'view_soa',
                                     'view_soa',
                                     'view_txt',
                                     'view_vlan',
                                     'view_assooption',
                                     'view_generaloption',
                                     'view_mailmessageoption',
                                     'view_optionalmachine',
                                     'view_optionaltopologie',
                                     'view_optionaluser',
                                     'view_service',
                                     'view_constructorswitch',
                                     'view_modelswitch',
                                     'view_port',
                                     'view_room',
                                     'view_stack',
                                     'view_switch',
                                     'add_adherent',
                                     'change_adherent',
                                     'view_ban',
                                     'add_club',
                                     'change_club',
                                     'view_listright',
                                     'add_school',
                                     'change_school',
                                     'delete_school',
                                     'view_school',
                                     'view_serviceuser',
                                     'add_user',
                                     'change_user',
                                     'change_user_force',
                                     'change_user_password',
                                     'view_user',
                                     'add_whitelist',
                                     'change_whitelist',
                                     'delete_whitelist',
                                     'view_whitelist'],
                         'tresorier': ['add_article',
                                       'change_article',
                                       'delete_article',
                                       'view_article',
                                       'add_banque',
                                       'change_banque',
                                       'delete_banque',
                                       'view_banque',
                                       'add_cotisation',
                                       'change_all_cotisation',
                                       'change_cotisation',
                                       'delete_cotisation',
                                       'view_cotisation',
                                       'add_facture',
                                       'can_change_control',
                                       'can_change_pdf',
                                       'can_create',
                                       'can_delete',
                                       'can_edit',
                                       'can_view',
                                       'can_view_all',
                                       'change_all_facture',
                                       'change_facture',
                                       'change_facture_control',
                                       'change_facture_pdf',
                                       'delete_facture',
                                       'view_facture',
                                       'add_paiement',
                                       'change_paiement',
                                       'delete_paiement',
                                       'view_paiement',
                                       'add_vente',
                                       'change_all_vente',
                                       'change_vente',
                                       'delete_vente',
                                       'view_vente'],
                         'admin': ['add_logentry',
                                   'change_logentry',
                                   'delete_logentry',
                                   'add_assooption',
                                   'change_assooption',
                                   'delete_assooption',
                                   'view_assooption',
                                   'add_generaloption',
                                   'change_generaloption',
                                   'delete_generaloption',
                                   'view_generaloption',
                                   'add_mailmessageoption',
                                   'change_mailmessageoption',
                                   'delete_mailmessageoption',
                                   'view_mailmessageoption',
                                   'add_optionalmachine',
                                   'change_optionalmachine',
                                   'delete_optionalmachine',
                                   'view_optionalmachine',
                                   'add_optionaltopologie',
                                   'change_optionaltopologie',
                                   'delete_optionaltopologie',
                                   'view_optionaltopologie',
                                   'add_optionaluser',
                                   'change_optionaluser',
                                   'delete_optionaluser',
                                   'view_optionaluser',
                                   'add_service',
                                   'add_services',
                                   'change_service',
                                   'change_services',
                                   'delete_service',
                                   'delete_services',
                                   'view_service'],
                         'infra': ['add_domain',
                                   'change_domain',
                                   'delete_domain',
                                   'view_domain',
                                   'add_extension',
                                   'change_extension',
                                   'delete_extension',
                                   'use_all_extension',
                                   'view_extension',
                                   'add_interface',
                                   'change_interface',
                                   'delete_interface',
                                   'view_interface',
                                   'add_iplist',
                                   'change_iplist',
                                   'delete_iplist',
                                   'view_iplist',
                                   'add_iptype',
                                   'change_iptype',
                                   'delete_iptype',
                                   'use_all_iptype',
                                   'view_iptype',
                                   'add_machine',
                                   'change_machine',
                                   'change_machine_user',
                                   'delete_machine',
                                   'view_machine',
                                   'add_machinetype',
                                   'change_machinetype',
                                   'delete_machinetype',
                                   'use_all_machinetype',
                                   'view_machinetype',
                                   'add_mx',
                                   'change_mx',
                                   'delete_mx',
                                   'view_mx',
                                   'add_nas',
                                   'change_nas',
                                   'delete_nas',
                                   'view_nas',
                                   'add_ns',
                                   'change_ns',
                                   'delete_ns',
                                   'view_ns',
                                   'add_ouvertureport',
                                   'change_ouvertureport',
                                   'delete_ouvertureport',
                                   'add_ouvertureportlist',
                                   'change_ouvertureportlist',
                                   'delete_ouvertureportlist',
                                   'view_ouvertureportlist',
                                   'add_service',
                                   'change_service',
                                   'delete_service',
                                   'view_service',
                                   'add_service_link',
                                   'change_service_link',
                                   'delete_service_link',
                                   'add_soa',
                                   'change_soa',
                                   'delete_soa',
                                   'view_soa',
                                   'add_srv',
                                   'change_srv',
                                   'delete_srv',
                                   'view_soa',
                                   'add_text',
                                   'add_txt',
                                   'change_text',
                                   'change_txt',
                                   'delete_text',
                                   'delete_txt',
                                   'view_txt',
                                   'add_vlan',
                                   'change_vlan',
                                   'delete_vlan',
                                   'view_vlan',
                                   'add_constructorswitch',
                                   'change_constructorswitch',
                                   'delete_constructorswitch',
                                   'view_constructorswitch',
                                   'add_modelswitch',
                                   'change_modelswitch',
                                   'delete_modelswitch',
                                   'view_modelswitch',
                                   'add_port',
                                   'change_port',
                                   'delete_port',
                                   'view_port',
                                   'add_room',
                                   'change_room',
                                   'delete_room',
                                   'view_room',
                                   'add_stack',
                                   'change_stack',
                                   'delete_stack',
                                   'view_stack',
                                   'add_switch',
                                   'change_switch',
                                   'delete_switch',
                                   'view_switch',
                                   'add_listshell',
                                   'change_listshell',
                                   'delete_listshell',
                                   'add_serviceuser',
                                   'change_serviceuser',
                                   'delete_serviceuser',
                                   'view_serviceuser',
                                   'change_user',
                                   'view_user']}

    rights = apps.get_model("users", "ListRight")
    permissions = apps.get_model("auth", "Permission")
    groups = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias
    for group in permission_groups:
        lr_object = rights.objects.using(db_alias).filter(
            unix_name=group).first()
        if not lr_object:
            last = rights.objects.using(db_alias).all().order_by('gid').last()
            if last:
                gid = last.gid + 1
            else:
                gid = 501
            group_object = groups.objects.using(db_alias).create(name=group)
            lr_object = rights.objects.using(db_alias).create(unix_name=group,
                                                              gid=gid,
                                                              group_ptr=group_object)
        lr_object = lr_object.group_ptr
        for permission in permission_groups[group]:
            perm = permissions.objects.using(db_alias).filter(
                codename=permission).first()
            if perm:
                lr_object.permissions.add(perm)
        lr_object.save()


def untransfer_permissions(apps, schema_editor):
    return


def transfer_permissions2(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    contenttype = apps.get_model("contenttypes", "ContentType")
    rights = apps.get_model("users", "ListRight")
    permissions = apps.get_model("auth", "Permission")
    groups = apps.get_model("auth", "Group")
    machine = apps.get_model("machines", "Machine")
    perm = permissions.objects.using(db_alias).filter(
        codename='serveur').first()
    if not perm:
        perm = permissions.objects.using(db_alias).create(
            codename='serveur',
            name='Serveur',
            content_type=contenttype.objects.get_for_model(machine)
        )
    group_object = rights.objects.using(db_alias).filter(
        unix_name='serveur').first()
    if not group_object:
        last_gid = rights.objects.using(db_alias).all().order_by(
            'gid').last().gid
        gid = last_gid + 1
        abstract_group = groups.objects.using(db_alias).create(name='serveur')
        group_object = rights.objects.using(db_alias).create(
            group_ptr=abstract_group, unix_name='serveur', gid=gid)
    group_object = group_object.group_ptr
    group_object.permissions.add(perm)
    group_object.save()


def untransfer_permissions2(apps, schema_editor):
    return


def transfer_permissions3(apps, schema_editor):
    critical_rights = ['adm', 'admin', 'bureau', 'infra', 'tresorier',
                       'serveur', 'bofh']
    db_alias = schema_editor.connection.alias
    rights = apps.get_model("users", "ListRight")
    for right in critical_rights:
        rg = rights.objects.using(db_alias).filter(unix_name=right).first()
        if rg:
            rg.critical = True
            rg.save()


def untransfer_permissions3(apps, schema_editor):
    return


def create_initial_email_address(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    User = apps.get_model("users", "User")
    EMailAddress = apps.get_model("users", "EMailAddress")
    users = User.objects.using(db_alias).all()
    for user in users:
        EMailAddress.objects.using(db_alias).create(
            local_part=user.pseudo,
            user=user
        )


def delete_all_email_address(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    EMailAddress = apps.get_model("users", "EMailAddress")
    EMailAddress.objects.using(db_alias).delete()


class Migration(migrations.Migration):
    replaces = [('users', '0001_initial'), ('users', '0002_auto_20160630_2301'),
                ('users', '0003_listrights_rights'),
                ('users', '0004_auto_20160701_2312'),
                ('users', '0005_auto_20160702_0006'), ('users', '0006_ban'),
                ('users', '0007_auto_20160702_2322'),
                ('users', '0008_user_registered'), ('users', '0009_user_room'),
                ('users', '0010_auto_20160703_1226'),
                ('users', '0011_auto_20160703_1227'),
                ('users', '0012_auto_20160703_1230'),
                ('users', '0013_auto_20160704_1547'),
                ('users', '0014_auto_20160704_1548'),
                ('users', '0015_whitelist'),
                ('users', '0016_auto_20160706_1220'),
                ('users', '0017_auto_20160707_0105'),
                ('users', '0018_auto_20160707_0115'),
                ('users', '0019_auto_20160708_1633'), ('users', '0020_request'),
                ('users', '0021_ldapuser'), ('users', '0022_ldapuser_sambasid'),
                ('users', '0023_auto_20160724_1908'),
                ('users', '0024_remove_ldapuser_mac_list'),
                ('users', '0025_listshell'), ('users', '0026_user_shell'),
                ('users', '0027_auto_20160726_0216'),
                ('users', '0028_auto_20160726_0227'),
                ('users', '0029_auto_20160726_0229'),
                ('users', '0030_auto_20160726_0357'),
                ('users', '0031_auto_20160726_0359'),
                ('users', '0032_auto_20160727_2122'),
                ('users', '0033_remove_ldapuser_loginshell'),
                ('users', '0034_auto_20161018_0037'),
                ('users', '0035_auto_20161018_0046'),
                ('users', '0036_auto_20161022_2146'),
                ('users', '0037_auto_20161028_1906'),
                ('users', '0038_auto_20161031_0258'),
                ('users', '0039_auto_20161119_0033'),
                ('users', '0040_auto_20161119_1709'),
                ('users', '0041_listright_details'),
                ('users', '0042_auto_20161126_2028'),
                ('users', '0043_auto_20161224_1156'),
                ('users', '0044_user_ssh_public_key'),
                ('users', '0043_ban_state'), ('users', '0045_merge'),
                ('users', '0046_auto_20170617_1433'),
                ('users', '0047_auto_20170618_0156'),
                ('users', '0048_auto_20170618_0210'),
                ('users', '0049_auto_20170618_1424'),
                ('users', '0050_serviceuser_comment'),
                ('users', '0051_user_telephone'),
                ('users', '0052_ldapuser_shadowexpire'),
                ('users', '0053_auto_20170626_2105'),
                ('users', '0054_auto_20170626_2219'),
                ('users', '0055_auto_20171003_0556'),
                ('users', '0056_auto_20171015_2033'),
                ('users', '0057_auto_20171023_0301'),
                ('users', '0058_auto_20171025_0154'),
                ('users', '0059_auto_20171025_1854'),
                ('users', '0060_auto_20171120_0317'),
                ('users', '0061_auto_20171230_2033'),
                ('users', '0062_auto_20171231_0056'),
                ('users', '0063_auto_20171231_0140'),
                ('users', '0064_auto_20171231_0150'),
                ('users', '0065_auto_20171231_2053'),
                ('users', '0066_grouppermissions'),
                ('users', '0067_serveurpermission'),
                ('users', '0068_auto_20180107_2245'),
                ('users', '0069_club_mailing'),
                ('users', '0070_auto_20180324_1906'),
                ('users', '0071_auto_20180415_1252'),
                ('users', '0072_auto_20180426_2021'),
                ('users', '0073_auto_20180629_1614'),
                ('users', '0074_auto_20180814_1059'),
                ('users', '0074_auto_20180810_2104'),
                ('users', '0075_merge_20180815_2202'),
                ('users', '0076_auto_20180818_1321'),
                ('users', '0077_auto_20180824_1750'),
                ('users', '0078_auto_20181011_1405'),
                ('users', '0079_auto_20181228_2039'),
                ('users', '0080_auto_20190108_1726'),
                ('users', '0081_auto_20190317_0302')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('surname', models.CharField(max_length=255)),
                ('pseudo', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(max_length=254)),
                ('promo', models.CharField(max_length=255)),
                ('pwd_ssha', models.CharField(max_length=255)),
                ('pwd_ntlm', models.CharField(max_length=255)),
                ('state', models.IntegerField(
                    choices=[(0, 'STATE_ACTIVE'), (1, 'STATE_DEACTIVATED'),
                             (2, 'STATE_ARCHIVED')], default=0)),
                ('school',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to='users.School')),
            ],
        ),
        migrations.CreateModel(
            name='ListRights',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('listright', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Right',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('right',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to='users.ListRights')),
                ('user',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RenameModel(
            old_name='ListRights',
            new_name='ListRight',
        ),
        migrations.AlterUniqueTogether(
            name='right',
            unique_together=set([('user', 'right')]),
        ),
        migrations.CreateModel(
            name='Ban',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('raison', models.CharField(max_length=255)),
                ('date_start', models.DateTimeField(auto_now_add=True)),
                ('date_end',
                 models.DateTimeField(help_text='%d/%m/%y %H:%M:%S')),
                ('user',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='registered',
            field=models.DateTimeField(auto_now_add=True,
                                       default=datetime.datetime(2016, 7, 2, 23,
                                                                 25, 21, 698883,
                                                                 tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='room',
            field=models.OneToOneField(blank=True, null=True,
                                       on_delete=django.db.models.deletion.PROTECT,
                                       to='topologie.Room'),
        ),
        migrations.AddField(
            model_name='user',
            name='comment',
            field=models.CharField(blank=True, help_text='Commentaire, promo',
                                   max_length=255),
        ),
        migrations.RemoveField(
            model_name='user',
            name='promo',
        ),
        migrations.CreateModel(
            name='Whitelist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('raison', models.CharField(max_length=255)),
                ('date_start', models.DateTimeField(auto_now_add=True)),
                ('date_end',
                 models.DateTimeField(help_text='%d/%m/%y %H:%M:%S')),
                ('user',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='pseudo',
            field=models.CharField(
                help_text='Doit contenir uniquement des lettres, chiffres, ou tirets',
                max_length=32, unique=True,
                validators=[users.models.linux_user_validator]),
        ),
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True,
                                       verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='user',
            name='password',
            field=models.CharField(default='!', max_length=128,
                                   verbose_name='password'),
            preserve_default=False,
        ),
        migrations.RunPython(
            code=move_passwords,
            reverse_code=django.db.migrations.operations.special.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name='user',
            name='pwd_ssha',
        ),
        migrations.AlterField(
            model_name='listright',
            name='listright',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('type', models.CharField(
                    choices=[('PW', 'Mot de passe'), ('EM', 'Email')],
                    max_length=2)),
                ('token', models.CharField(max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('user',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LdapUser',
            fields=[
                ('dn', models.CharField(max_length=200, primary_key=True,
                                        serialize=False)),
                ('gid',
                 ldapdb.models.fields.IntegerField(db_column='gidNumber')),
                ('name',
                 ldapdb.models.fields.CharField(db_column='cn', max_length=200,
                                                primary_key=True,
                                                serialize=False)),
                ('uid', ldapdb.models.fields.CharField(db_column='uid',
                                                       max_length=200)),
                ('uidNumber',
                 ldapdb.models.fields.IntegerField(db_column='uidNumber',
                                                   unique=True)),
                ('sn', ldapdb.models.fields.CharField(db_column='sn',
                                                      max_length=200)),
                ('mail', ldapdb.models.fields.CharField(db_column='mail',
                                                        max_length=200)),
                ('given_name',
                 ldapdb.models.fields.CharField(db_column='givenName',
                                                max_length=200)),
                ('home_directory',
                 ldapdb.models.fields.CharField(db_column='homeDirectory',
                                                max_length=200)),
                ('dialupAccess',
                 ldapdb.models.fields.CharField(db_column='dialupAccess',
                                                max_length=200)),
                ('sambaSID',
                 ldapdb.models.fields.IntegerField(db_column='sambaSID',
                                                   unique=True)),
                ('display_name', ldapdb.models.fields.CharField(blank=True,
                                                                db_column='displayName',
                                                                max_length=200,
                                                                null=True)),
                ('macs', ldapdb.models.fields.ListField(blank=True,
                                                        db_column='radiusCallingStationId',
                                                        max_length=200,
                                                        null=True)),
                ('sambat_nt_password',
                 ldapdb.models.fields.CharField(blank=True,
                                                db_column='sambaNTPassword',
                                                max_length=200, null=True)),
                ('user_password', ldapdb.models.fields.CharField(blank=True,
                                                                 db_column='userPassword',
                                                                 max_length=200,
                                                                 null=True)),
                ('login_shell', ldapdb.models.fields.CharField(blank=True,
                                                               db_column='loginShell',
                                                               max_length=200,
                                                               null=True)),
                ('shadowexpire', ldapdb.models.fields.CharField(blank=True,
                                                                db_column='shadowExpire',
                                                                max_length=200,
                                                                null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ListShell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('shell', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='shell',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='users.ListShell'),
        ),
        migrations.CreateModel(
            name='LdapUserGroup',
            fields=[
                ('dn', models.CharField(max_length=200, primary_key=True,
                                        serialize=False)),
                ('gid',
                 ldapdb.models.fields.IntegerField(db_column='gidNumber')),
                ('members', ldapdb.models.fields.ListField(blank=True,
                                                           db_column='memberUid')),
                ('name',
                 ldapdb.models.fields.CharField(db_column='cn', max_length=200,
                                                primary_key=True,
                                                serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='listright',
            name='gid',
            field=models.PositiveIntegerField(null=True, unique=True),
        ),
        migrations.CreateModel(
            name='LdapServiceUser',
            fields=[
                ('dn', models.CharField(max_length=200, primary_key=True,
                                        serialize=False)),
                ('name',
                 ldapdb.models.fields.CharField(db_column='cn', max_length=200,
                                                primary_key=True,
                                                serialize=False)),
                ('user_password', ldapdb.models.fields.CharField(blank=True,
                                                                 db_column='userPassword',
                                                                 max_length=200,
                                                                 null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('password',
                 models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True,
                                                    verbose_name='last login')),
                ('pseudo', models.CharField(
                    help_text='Doit contenir uniquement des lettres, chiffres, ou tirets',
                    max_length=32, unique=True,
                    validators=[users.models.linux_user_validator])),
                ('access_group', models.CharField(
                    choices=[('auth', 'auth'), ('readonly', 'readonly'),
                             ('usermgmt', 'usermgmt')], default='readonly',
                    max_length=32)),
                ('comment',
                 models.CharField(blank=True, help_text='Commentaire',
                                  max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='user',
            name='rezo_rez_uid',
            field=models.PositiveIntegerField(blank=True, null=True,
                                              unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='uid_number',
            field=models.PositiveIntegerField(
                default=users.models.get_fresh_user_uid, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='school',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='users.School'),
        ),
        migrations.AlterField(
            model_name='user',
            name='state',
            field=models.IntegerField(
                choices=[(0, 'STATE_ACTIVE'), (1, 'STATE_DISABLED'),
                         (2, 'STATE_ARCHIVE')], default=0),
        ),
        migrations.AddField(
            model_name='listright',
            name='details',
            field=models.CharField(blank=True, help_text='Description',
                                   max_length=255),
        ),
        migrations.AddField(
            model_name='ban',
            name='state',
            field=models.IntegerField(choices=[(0, 'HARD (aucun accès)'), (
                1, 'SOFT (accès local seulement)'), (2,
                                                     'BRIDAGE (bridage du débit)')],
                                      default=0),
        ),
        migrations.CreateModel(
            name='LdapServiceUserGroup',
            fields=[
                ('dn', models.CharField(max_length=200, primary_key=True,
                                        serialize=False)),
                ('name',
                 ldapdb.models.fields.CharField(db_column='cn', max_length=200,
                                                primary_key=True,
                                                serialize=False)),
                ('members', ldapdb.models.fields.ListField(blank=True,
                                                           db_column='member')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='user',
            name='telephone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='listright',
            name='listright',
            field=models.CharField(max_length=255, unique=True, validators=[
                django.core.validators.RegexValidator('^[a-z]+$',
                                                      message='Les groupes unix ne peuvent contenir que des lettres minuscules')]),
        ),
        migrations.AlterField(
            model_name='listright',
            name='listright',
            field=models.CharField(max_length=255, unique=True, validators=[
                django.core.validators.RegexValidator('^[a-z]+$',
                                                      message='Les groupes unix ne peuvent contenir            que des lettres minuscules')]),
        ),
        migrations.CreateModel(
            name='Adherent',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True,
                                                  on_delete=django.db.models.deletion.CASCADE,
                                                  parent_link=True,
                                                  primary_key=True,
                                                  serialize=False,
                                                  to=settings.AUTH_USER_MODEL)),
                ('usname', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('users.user',),
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True,
                                                  on_delete=django.db.models.deletion.CASCADE,
                                                  parent_link=True,
                                                  primary_key=True,
                                                  serialize=False,
                                                  to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('users.user',),
        ),
        migrations.RunSQL(
            sql='insert into users_adherent (user_ptr_id, usname) select id, name from users_user',
            reverse_sql='insert into users_user (name) select usname from users_adherent',
        ),
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
        migrations.RenameField(
            model_name='adherent',
            old_name='usname',
            new_name='name',
        ),
        migrations.AddField(
            model_name='adherent',
            name='room_adherent',
            field=models.OneToOneField(blank=True, null=True,
                                       on_delete=django.db.models.deletion.PROTECT,
                                       to='topologie.Room'),
        ),
        migrations.AddField(
            model_name='club',
            name='room_club',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='topologie.Room'),
        ),
        migrations.RunPython(
            code=create_move_room,
            reverse_code=delete_move_room,
        ),
        migrations.RemoveField(
            model_name='user',
            name='room',
        ),
        migrations.RenameField(
            model_name='adherent',
            old_name='room_adherent',
            new_name='room',
        ),
        migrations.RenameField(
            model_name='club',
            old_name='room_club',
            new_name='room',
        ),
        migrations.AddField(
            model_name='club',
            name='administrators',
            field=models.ManyToManyField(blank=True,
                                         related_name='club_administrator',
                                         to='users.Adherent'),
        ),
        migrations.AddField(
            model_name='club',
            name='members',
            field=models.ManyToManyField(blank=True,
                                         related_name='club_members',
                                         to='users.Adherent'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True,
                                         help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                                         related_name='user_set',
                                         related_query_name='user',
                                         to='auth.Group',
                                         verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False,
                                      help_text='Designates that this user has all permissions without explicitly assigning them.',
                                      verbose_name='superuser status'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True,
                                         help_text='Specific permissions for this user.',
                                         related_name='user_set',
                                         related_query_name='user',
                                         to='auth.Permission',
                                         verbose_name='user permissions'),
        ),
        migrations.RenameField(
            model_name='listright',
            old_name='listright',
            new_name='unix_name',
        ),
        migrations.AddField(
            model_name='listright',
            name='group_ptr',
            field=models.OneToOneField(auto_created=True, blank=True, null=True,
                                       on_delete=django.db.models.deletion.CASCADE,
                                       serialize=False, to='auth.Group'),
            preserve_default=False,
        ),
        migrations.RunPython(
            code=create_groups,
            reverse_code=delete_groups,
        ),
        migrations.RunPython(
            code=transfer_right,
            reverse_code=untransfer_right,
        ),
        migrations.AlterUniqueTogether(
            name='right',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='right',
            name='right',
        ),
        migrations.RemoveField(
            model_name='right',
            name='user',
        ),
        migrations.DeleteModel(
            name='Right',
        ),
        migrations.RemoveField(
            model_name='listright',
            name='id',
        ),
        migrations.AlterField(
            model_name='listright',
            name='group_ptr',
            field=models.OneToOneField(auto_created=True,
                                       on_delete=django.db.models.deletion.CASCADE,
                                       parent_link=True, primary_key=True,
                                       serialize=False, to='auth.Group'),
        ),
        migrations.AlterModelOptions(
            name='ban',
            options={'permissions': (
                ('view_ban', "Peut voir un objet ban quelqu'il soit"),)},
        ),
        migrations.AlterModelOptions(
            name='listright',
            options={'permissions': (
                ('view_listright', 'Peut voir un objet Group/ListRight'),)},
        ),
        migrations.AlterModelOptions(
            name='school',
            options={
                'permissions': (('view_school', 'Peut voir un objet school'),)},
        ),
        migrations.AlterModelOptions(
            name='serviceuser',
            options={'permissions': (
                ('view_serviceuser', 'Peut voir un objet serviceuser'),)},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (
                ('change_user_password',
                 "Peut changer le mot de passe d'un user"),
                ('change_user_state', "Peut éditer l'etat d'un user"),
                ('change_user_force', 'Peut forcer un déménagement'),
                ('change_user_shell', "Peut éditer le shell d'un user"), (
                    'change_user_groups',
                    "Peut éditer les groupes d'un user ! Permission critique"),
                ('view_user', 'Peut voir un objet user quelquonque'))},
        ),
        migrations.AlterModelOptions(
            name='whitelist',
            options={'permissions': (
                ('view_whitelist', 'Peut voir un objet whitelist'),)},
        ),
        migrations.RunPython(
            code=transfer_permissions,
            reverse_code=untransfer_permissions,
        ),
        migrations.RunPython(
            code=transfer_permissions2,
            reverse_code=untransfer_permissions2,
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (
                ('change_user_password',
                 "Peut changer le mot de passe d'un user"),
                ('change_user_state', "Peut éditer l'etat d'un user"),
                ('change_user_force', 'Peut forcer un déménagement'),
                ('change_user_shell', "Peut éditer le shell d'un user"), (
                    'change_user_groups',
                    "Peut éditer les groupes d'un user ! Permission critique"),
                (
                    'change_all_users',
                    'Peut éditer tous les users, y compris ceux dotés de droits. Superdroit'),
                ('view_user', 'Peut voir un objet user quelquonque'))},
        ),
        migrations.AddField(
            model_name='listright',
            name='critical',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(
            code=transfer_permissions3,
            reverse_code=untransfer_permissions3,
        ),
        migrations.AddField(
            model_name='club',
            name='mailing',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelOptions(
            name='listshell',
            options={'permissions': (
                (
                    'view_listshell',
                    "Peut voir un objet shell quelqu'il soit"),)},
        ),
        migrations.AlterField(
            model_name='listright',
            name='unix_name',
            field=models.CharField(max_length=255, unique=True, validators=[
                django.core.validators.RegexValidator('^[a-z]+$',
                                                      message='Les groupes unix ne peuvent contenir que des lettres minuscules')]),
        ),
        migrations.AlterField(
            model_name='ban',
            name='date_end',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='whitelist',
            name='date_end',
            field=models.DateTimeField(),
        ),
        migrations.CreateModel(
            name='EMailAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('local_part',
                 models.CharField(help_text='Local part of the email address',
                                  max_length=128, unique=True)),
                ('user', models.ForeignKey(help_text='User of the local email',
                                           on_delete=django.db.models.deletion.CASCADE,
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (
                    ('view_emailaddress',
                     'Can see a local email account object'),),
                'verbose_name': 'Local email account',
                'verbose_name_plural': 'Local email accounts',
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.AddField(
            model_name='user',
            name='local_email_enabled',
            field=models.BooleanField(default=False,
                                      help_text='Wether or not to enable the local email account.'),
        ),
        migrations.AddField(
            model_name='user',
            name='local_email_redirect',
            field=models.BooleanField(default=False,
                                      help_text='Whether or not to redirect the local email messages to the main email.'),
        ),
        migrations.RunPython(
            code=create_initial_email_address,
            reverse_code=delete_all_email_address,
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True,
                                    help_text='External email address allowing us to contact you.',
                                    max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='local_email_enabled',
            field=models.BooleanField(default=False,
                                      help_text='Enable the local email account.'),
        ),
        migrations.AlterField(
            model_name='user',
            name='local_email_redirect',
            field=models.BooleanField(default=False,
                                      help_text='Enable redirection of the local email messages to the main email.'),
        ),
        migrations.AddField(
            model_name='adherent',
            name='gpg_fingerprint',
            field=models.CharField(blank=True, max_length=40, null=True,
                                   validators=[
                                       django.core.validators.RegexValidator(
                                           '^[0-9A-F]{40}$',
                                           message='Une fingerprint GPG doit contenir 40 caractères hexadécimaux')]),
        ),
        migrations.AlterModelOptions(
            name='adherent',
            options={'verbose_name': 'member',
                     'verbose_name_plural': 'members'},
        ),
        migrations.AlterModelOptions(
            name='ban',
            options={'permissions': (('view_ban', 'Can view a ban object'),),
                     'verbose_name': 'ban', 'verbose_name_plural': 'bans'},
        ),
        migrations.AlterModelOptions(
            name='club',
            options={'verbose_name': 'club', 'verbose_name_plural': 'clubs'},
        ),
        migrations.AlterModelOptions(
            name='emailaddress',
            options={'permissions': (
                (
                    'view_emailaddress',
                    'Can view a local email account object'),),
                'verbose_name': 'local email account',
                'verbose_name_plural': 'local email accounts'},
        ),
        migrations.AlterModelOptions(
            name='listright',
            options={'permissions': (
                ('view_listright', 'Can view a group of rights object'),),
                'verbose_name': 'group of rights',
                'verbose_name_plural': 'groups of rights'},
        ),
        migrations.AlterModelOptions(
            name='listshell',
            options={
                'permissions': (('view_listshell', 'Can view a shell object'),),
                'verbose_name': 'shell', 'verbose_name_plural': 'shells'},
        ),
        migrations.AlterModelOptions(
            name='school',
            options={
                'permissions': (('view_school', 'Can view a school object'),),
                'verbose_name': 'school', 'verbose_name_plural': 'schools'},
        ),
        migrations.AlterModelOptions(
            name='serviceuser',
            options={'permissions': (
                ('view_serviceuser', 'Can view a service user object'),),
                'verbose_name': 'service user',
                'verbose_name_plural': 'service users'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (
                ('change_user_password', 'Can change the password of a user'),
                ('change_user_state', 'Can edit the state of a user'),
                ('change_user_force', 'Can force the move'),
                ('change_user_shell', 'Can edit the shell of a user'), (
                    'change_user_groups',
                    'Can edit the groups of rights of a user (critical permission)'),
                (
                    'change_all_users',
                    'Can edit all users, including those with rights.'),
                ('view_user', 'Can view a user object')),
                'verbose_name': 'user (member or club)',
                'verbose_name_plural': 'users (members or clubs)'},
        ),
        migrations.AlterModelOptions(
            name='whitelist',
            options={
                'permissions': (
                    ('view_whitelist', 'Can view a whitelist object'),),
                'verbose_name': 'whitelist (free of charge access)',
                'verbose_name_plural': 'whitelists (free of charge access)'},
        ),
        migrations.AlterField(
            model_name='adherent',
            name='gpg_fingerprint',
            field=models.CharField(blank=True, max_length=40, null=True,
                                   validators=[
                                       django.core.validators.RegexValidator(
                                           '^[0-9A-F]{40}$',
                                           message='A GPG fingerprint must contain 40 hexadecimal characters.')]),
        ),
        migrations.AlterField(
            model_name='ban',
            name='state',
            field=models.IntegerField(
                choices=[(0, 'HARD (no access)'),
                         (1, 'SOFT (local access only)'),
                         (2, 'RESTRICTED (speed limitation)')], default=0),
        ),
        migrations.AlterField(
            model_name='emailaddress',
            name='user',
            field=models.ForeignKey(help_text='User of the local email account',
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='listright',
            name='unix_name',
            field=models.CharField(max_length=255, unique=True, validators=[
                django.core.validators.RegexValidator('^[a-z]+$',
                                                      message='UNIX groups can only contain lower case letters.')]),
        ),
        migrations.AlterField(
            model_name='request',
            name='type',
            field=models.CharField(
                choices=[('PW', 'Password'), ('EM', 'Email address')],
                max_length=2),
        ),
        migrations.AlterField(
            model_name='serviceuser',
            name='comment',
            field=models.CharField(blank=True, help_text='Comment',
                                   max_length=255),
        ),
        migrations.AlterField(
            model_name='serviceuser',
            name='pseudo',
            field=models.CharField(
                help_text='Must only contain letters, numerals or dashes.',
                max_length=32, unique=True,
                validators=[users.models.linux_user_validator]),
        ),
        migrations.AlterField(
            model_name='user',
            name='comment',
            field=models.CharField(blank=True, help_text='Comment, school year',
                                   max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='local_email_redirect',
            field=models.BooleanField(default=False,
                                      help_text='Enable redirection of the local email messages to the main email address.'),
        ),
        migrations.AlterField(
            model_name='user',
            name='pseudo',
            field=models.CharField(
                help_text='Must only contain letters, numerals or dashes.',
                max_length=32, unique=True,
                validators=[users.models.linux_user_validator]),
        ),
        migrations.AlterField(
            model_name='user',
            name='state',
            field=models.IntegerField(
                choices=[(0, 'STATE_ACTIVE'), (1, 'STATE_DISABLED'),
                         (2, 'STATE_ARCHIVE'), (3, 'STATE_NOT_YET_ACTIVE')],
                default=3),
        ),
        migrations.AlterField(
            model_name='request',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='adherent',
            name='gpg_fingerprint',
            field=models.CharField(blank=True, max_length=49, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='state',
            field=models.IntegerField(
                choices=[(0, 'Active'), (1, 'Disabled'), (2, 'Archived'),
                         (3, 'Not yet active')], default=3),
        ),
        migrations.AlterField(
            model_name='user',
            name='state',
            field=models.IntegerField(
                choices=[(0, 'Active'), (1, 'Disabled'), (2, 'Archived'),
                         (3, 'Not yet active'), (4, 'Full Archived')],
                default=3),
        ),
    ]
