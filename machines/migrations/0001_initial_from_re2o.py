# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2019  Alexandre Iooss

from __future__ import unicode_literals

import datetime

import django.core.validators
import django.db.models.deletion
import macaddress.fields
from django.conf import settings
from django.db import migrations, models

import machines.models
import re2o.mixins


def rename_permission_soa_to_srv(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    # The Permission called 'view_soa' but in the Srv object
    try:
        to_rename = Permission.objects.get(
            codename='view_soa',
            content_type__model='srv'
        )
    except Permission.DoesNotExist:
        # The permission is missing so no problem
        pass
    else:
        to_rename.name = 'Peut voir un object srv'
        to_rename.codename = 'view_srv'
        to_rename.save()


def remove_permission_alias(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    for codename in ['add_alias', 'change_alias', 'delete_alias']:
        # Retrieve the wrong permission
        try:
            to_remove = Permission.objects.get(
                codename=codename,
                content_type__model='domain'
            )
        except Permission.DoesNotExist:
            # The permission is missing so no problem
            pass
        else:
            to_remove.delete()


def remove_permission_text(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    for codename in ['add_text', 'change_text', 'delete_text']:
        # Retrieve the wrong permission
        try:
            to_remove = Permission.objects.get(
                codename=codename,
                content_type__model='txt'
            )
        except Permission.DoesNotExist:
            # The permission is missing so no problem
            pass
        else:
            to_remove.delete()


def migrate(apps, schema_editor):
    Role = apps.get_model('machines', 'Role')

    for role in Role.objects.filter(specific_role='dns-recursif-server'):
        role.specific_role = 'dns-recursive-server'
        role.save()


class Migration(migrations.Migration):
    replaces = [('machines', '0001_initial'),
                ('machines', '0002_auto_20160703_1444'),
                ('machines', '0003_auto_20160703_1450'),
                ('machines', '0004_auto_20160703_1451'),
                ('machines', '0005_auto_20160703_1523'),
                ('machines', '0006_auto_20160703_1813'),
                ('machines', '0007_auto_20160703_1816'),
                ('machines', '0008_remove_interface_ipv6'),
                ('machines', '0009_auto_20160703_2358'),
                ('machines', '0010_auto_20160704_0104'),
                ('machines', '0011_auto_20160704_0105'),
                ('machines', '0012_auto_20160704_0118'),
                ('machines', '0013_auto_20160705_1014'),
                ('machines', '0014_auto_20160706_1220'),
                ('machines', '0015_auto_20160707_0105'),
                ('machines', '0016_auto_20160708_1633'),
                ('machines', '0017_auto_20160708_1645'),
                ('machines', '0018_auto_20160708_1813'),
                ('machines', '0019_auto_20160718_1141'),
                ('machines', '0020_auto_20160718_1849'),
                ('machines', '0021_auto_20161006_1943'),
                ('machines', '0022_auto_20161011_1829'),
                ('machines', '0023_iplist_ip_type'),
                ('machines', '0024_machinetype_need_infra'),
                ('machines', '0025_auto_20161023_0038'),
                ('machines', '0026_auto_20161026_1348'),
                ('machines', '0027_alias'),
                ('machines', '0028_iptype_domaine_ip'),
                ('machines', '0029_iptype_domaine_range'),
                ('machines', '0030_auto_20161118_1730'),
                ('machines', '0031_auto_20161119_1709'),
                ('machines', '0032_auto_20161119_1850'),
                ('machines', '0033_extension_need_infra'),
                ('machines', '0034_iplist_need_infra'),
                ('machines', '0035_auto_20161224_1201'),
                ('machines', '0036_auto_20161224_1204'),
                ('machines', '0037_domain_cname'),
                ('machines', '0038_auto_20161224_1721'),
                ('machines', '0039_auto_20161224_1732'),
                ('machines', '0040_remove_interface_dns'),
                ('machines', '0041_remove_ns_interface'),
                ('machines', '0042_ns_ns'),
                ('machines', '0043_auto_20170721_0350'),
                ('machines', '0044_auto_20170808_0233'),
                ('machines', '0045_auto_20170808_0348'),
                ('machines', '0046_auto_20170808_1423'),
                ('machines', '0047_auto_20170809_0606'),
                ('machines', '0048_auto_20170823_2315'),
                ('machines', '0049_vlan'),
                ('machines', '0050_auto_20170826_0022'),
                ('machines', '0051_iptype_vlan'),
                ('machines', '0052_auto_20170828_2322'),
                ('machines', '0053_text'), ('machines', '0054_text_zone'),
                ('machines', '0055_nas'),
                ('machines', '0056_nas_port_access_mode'),
                ('machines', '0057_nas_autocapture_mac'),
                ('machines', '0058_auto_20171002_0350'),
                ('machines', '0059_iptype_prefix_v6'),
                ('machines', '0060_iptype_ouverture_ports'),
                ('machines', '0061_auto_20171015_2033'),
                ('machines', '0062_extension_origin_v6'),
                ('machines', '0063_auto_20171020_0040'),
                ('machines', '0064_auto_20171115_0253'),
                ('machines', '0065_auto_20171115_1514'),
                ('machines', '0066_srv'),
                ('machines', '0067_auto_20171116_0152'),
                ('machines', '0068_auto_20171116_0252'),
                ('machines', '0069_auto_20171116_0822'),
                ('machines', '0070_auto_20171231_1947'),
                ('machines', '0071_auto_20171231_2100'),
                ('machines', '0072_auto_20180108_1822'),
                ('machines', '0073_auto_20180128_2203'),
                ('machines', '0074_auto_20180129_0352'),
                ('machines', '0075_auto_20180130_0052'),
                ('machines', '0076_auto_20180130_1623'),
                ('machines', '0077_auto_20180409_2243'),
                ('machines', '0078_auto_20180415_1252'),
                ('machines', '0079_auto_20180416_0107'),
                ('machines', '0080_auto_20180502_2334'),
                ('machines', '0081_auto_20180521_1413'),
                ('machines', '0082_auto_20180525_2209'),
                ('machines', '0083_remove_duplicate_rights'),
                ('machines', '0084_dname'), ('machines', '0085_sshfingerprint'),
                ('machines', '0086_role'), ('machines', '0087_dnssec'),
                ('machines', '0088_iptype_prefix_v6_length'),
                ('machines', '0089_auto_20180805_1148'),
                ('machines', '0090_auto_20180805_1459'),
                ('machines', '0091_auto_20180806_2310'),
                ('machines', '0092_auto_20180807_0926'),
                ('machines', '0093_auto_20180807_1115'),
                ('machines', '0094_auto_20180815_1918'),
                ('machines', '0095_auto_20180919_2225'),
                ('machines', '0096_auto_20181013_1417'),
                ('machines', '0097_extension_dnssec'),
                ('machines', '0098_auto_20190102_1745'),
                ('machines', '0099_role_recursive_dns'),
                ('machines', '0100_auto_20190102_1753'),
                ('machines', '0101_auto_20190108_1623'),
                ('machines', '0102_auto_20190303_1611')]

    dependencies = [
        ('users', '0005_auto_20160702_0006'),
        ('reversion', '0001_squashed_0004_auto_20160611_1202'),
    ]

    operations = [
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('user',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to=settings.AUTH_USER_MODEL)),
                ('name', models.CharField(blank=True, help_text='Optionnel',
                                          max_length=255, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'permissions': (
                    ('view_machine', 'Peut voir un objet machine quelquonque'),
                    (
                        'change_machine_user',
                        "Peut changer le propriétaire d'une machine")),
            },
        ),
        migrations.CreateModel(
            name='MachineType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Interface',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('ipv6', models.GenericIPAddressField(protocol='IPv6')),
                (
                    'mac_address',
                    macaddress.fields.MACAddressField(integer=True)),
                ('details', models.CharField(max_length=255)),
                ('name',
                 models.CharField(blank=True, max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='IpList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('ipv4',
                 models.GenericIPAddressField(protocol='IPv4', unique=True)),
                ('ip_type',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='machines.IpType')),
            ],
            options={
                'permissions': (('view_iplist', 'Peut voir un objet iplist'),),
            },
        ),
        migrations.AddField(
            model_name='interface',
            name='ipv4',
            field=models.OneToOneField(blank=True, null=True,
                                       on_delete=django.db.models.deletion.PROTECT,
                                       to='machines.IpList'),
        ),
        migrations.AddField(
            model_name='interface',
            name='machine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to='machines.Machine'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='mac_address',
            field=macaddress.fields.MACAddressField(integer=True, unique=True),
        ),
        migrations.RenameField(
            model_name='interface',
            old_name='name',
            new_name='dns',
        ),
        migrations.AlterField(
            model_name='interface',
            name='details',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.RemoveField(
            model_name='interface',
            name='ipv6',
        ),
        migrations.AlterField(
            model_name='interface',
            name='mac_address',
            field=macaddress.fields.MACAddressField(integer=False,
                                                    max_length=17, unique=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(help_text='Obligatoire et unique',
                                   max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(
                help_text='Obligatoire et unique, doit se terminer en .rez et ne pas comporter de points',
                max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(
                help_text="Obligatoire et unique, doit se terminer en .rez et ne pas comporter d'autres points",
                max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(
                help_text="Obligatoire et unique, doit se terminer en .example et ne pas comporter d'autres points",
                max_length=255, unique=True),
        ),
        migrations.CreateModel(
            name='Extension',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(
                help_text="Obligatoire et unique, doit se terminer en .rez et ne pas comporter d'autres points",
                max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(
                help_text="Obligatoire et unique, doit se terminer en .rez et ne pas comporter d'autres points",
                max_length=255, unique=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='type',
            field=models.ForeignKey(default=1,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='machines.MachineType'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(
                help_text="Obligatoire et unique, doit se terminer par exemple en .rez et ne pas comporter d'autres points",
                max_length=255, unique=True),
        ),
        migrations.CreateModel(
            name='IpType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=255)),
                ('need_infra', models.BooleanField(default=False)),
                ('extension',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to='machines.Extension')),
                ('domaine_ip', models.GenericIPAddressField(protocol='IPv4')),
                ('domaine_range', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(16),
                                django.core.validators.MaxValueValidator(32)])),
            ],
        ),
        migrations.AddField(
            model_name='machinetype',
            name='ip_type',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='machines.IpType'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='dns',
            field=models.CharField(
                help_text='Obligatoire et unique, ne doit pas comporter de points',
                max_length=255, unique=True),
        ),
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('alias', models.CharField(
                    help_text='Obligatoire et unique, ne doit pas comporter de points',
                    max_length=255)),
                ('interface_parent',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='machines.Interface')),
                ('extension', models.ForeignKey(default=1,
                                                on_delete=django.db.models.deletion.PROTECT,
                                                to='machines.Extension')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='alias',
            unique_together=set([('alias', 'extension')]),
        ),
        migrations.CreateModel(
            name='Mx',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(unique=True)),
                ('name', models.OneToOneField(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='machines.Alias')),
                ('zone',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to='machines.Extension')),
            ],
            options={
                'permissions': (('view_mx', 'Peut voir un objet mx'),),
            },
        ),
        migrations.CreateModel(
            name='Ns',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('zone',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to='machines.Extension')),
            ],
        ),
        migrations.AddField(
            model_name='extension',
            name='origin',
            field=models.OneToOneField(blank=True, null=True,
                                       on_delete=django.db.models.deletion.PROTECT,
                                       to='machines.IpList'),
        ),
        migrations.AlterField(
            model_name='extension',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AddField(
            model_name='extension',
            name='need_infra',
            field=models.BooleanField(default=False),
        ),
        migrations.RenameModel(
            old_name='Alias',
            new_name='Domain',
        ),
        migrations.RenameField(
            model_name='domain',
            old_name='alias',
            new_name='name',
        ),
        migrations.AlterField(
            model_name='domain',
            name='interface_parent',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to='machines.Interface'),
        ),
        migrations.AddField(
            model_name='domain',
            name='cname',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='related_domain',
                                    to='machines.Domain'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='interface_parent',
            field=models.OneToOneField(blank=True, null=True,
                                       on_delete=django.db.models.deletion.CASCADE,
                                       to='machines.Interface'),
        ),
        migrations.AlterUniqueTogether(
            name='domain',
            unique_together=set([('name', 'extension')]),
        ),
        migrations.RemoveField(
            model_name='interface',
            name='dns',
        ),
        migrations.AddField(
            model_name='ns',
            name='ns',
            field=models.OneToOneField(default=1,
                                       on_delete=django.db.models.deletion.PROTECT,
                                       to='machines.Domain'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('service_type',
                 models.CharField(blank=True, max_length=255, unique=True)),
                ('time_regen', models.DurationField()),
            ],
        ),
        migrations.CreateModel(
            name='Service_link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('last_regen', models.DateTimeField(auto_now_add=True)),
                ('asked_regen', models.BooleanField(default=False)),
                ('server',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='machines.Interface')),
                ('service',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='machines.Service')),
            ],
        ),
        migrations.AddField(
            model_name='service',
            name='servers',
            field=models.ManyToManyField(through='machines.Service_link',
                                         to='machines.Interface'),
        ),
        migrations.RemoveField(
            model_name='service',
            name='time_regen',
        ),
        migrations.AddField(
            model_name='service',
            name='min_time_regen',
            field=models.DurationField(default=datetime.timedelta(0, 60),
                                       help_text='Temps minimal avant nouvelle génération du service'),
        ),
        migrations.AddField(
            model_name='service',
            name='regular_time_regen',
            field=models.DurationField(default=datetime.timedelta(0, 3600),
                                       help_text='Temps maximal avant nouvelle génération du service'),
        ),
        migrations.CreateModel(
            name='Vlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('vlan_id', models.PositiveIntegerField(validators=[
                    django.core.validators.MaxValueValidator(4095)])),
                ('name', models.CharField(max_length=256)),
                ('comment', models.CharField(blank=True, max_length=256)),
            ],
            options={
                'permissions': (('view_vlan', 'Peut voir un objet vlan'),),
            },
        ),
        migrations.AddField(
            model_name='iptype',
            name='vlan',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='machines.Vlan'),
        ),
        migrations.RenameField(
            model_name='iptype',
            old_name='domaine_ip',
            new_name='domaine_ip_start',
        ),
        migrations.RemoveField(
            model_name='iptype',
            name='domaine_range',
        ),
        migrations.AddField(
            model_name='iptype',
            name='domaine_ip_stop',
            field=models.GenericIPAddressField(default='255.255.254.254',
                                               protocol='IPv4'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Txt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('field1', models.CharField(max_length=255)),
                ('field2', models.TextField(max_length=2047)),
                ('zone',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to='machines.Extension')),
            ],
            options={
                'permissions': (('view_txt', 'Peut voir un objet txt'),),
            },
        ),
        migrations.CreateModel(
            name='Nas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('machine_type',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   related_name='machinetype_on_nas',
                                   to='machines.MachineType')),
                ('nas_type',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   related_name='nas_type',
                                   to='machines.MachineType')),
                ('port_access_mode', models.CharField(
                    choices=[('802.1X', '802.1X'),
                             ('Mac-address', 'Mac-address')], default='802.1X',
                    max_length=32)),
                ('autocapture_mac', models.BooleanField(default=False)),
            ],
            options={
                'permissions': (('view_nas', 'Peut voir un objet Nas'),),
            },
        ),
        migrations.CreateModel(
            name='OuverturePort',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('begin', models.IntegerField()),
                ('end', models.IntegerField()),
                ('protocole',
                 models.CharField(choices=[('T', 'TCP'), ('U', 'UDP')],
                                  default='T', max_length=1)),
                ('io', models.CharField(choices=[('I', 'IN'), ('O', 'OUT')],
                                        default='O', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='OuverturePortList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    help_text='Nom de la configuration des ports.',
                    max_length=255)),
            ],
            options={
                'permissions': (('view_ouvertureportlist',
                                 'Peut voir un objet ouvertureport'),),
            },
        ),
        migrations.AddField(
            model_name='ouvertureport',
            name='port_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to='machines.OuverturePortList'),
        ),
        migrations.AddField(
            model_name='interface',
            name='port_lists',
            field=models.ManyToManyField(blank=True,
                                         to='machines.OuverturePortList'),
        ),
        migrations.AddField(
            model_name='iptype',
            name='prefix_v6',
            field=models.GenericIPAddressField(blank=True, null=True,
                                               protocol='IPv6'),
        ),
        migrations.AddField(
            model_name='iptype',
            name='ouverture_ports',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to='machines.OuverturePortList'),
        ),
        migrations.AlterField(
            model_name='ouvertureport',
            name='begin',
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MaxValueValidator(65535)]),
        ),
        migrations.AlterField(
            model_name='ouvertureport',
            name='end',
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MaxValueValidator(65535)]),
        ),
        migrations.AddField(
            model_name='extension',
            name='origin_v6',
            field=models.GenericIPAddressField(blank=True, null=True,
                                               protocol='IPv6'),
        ),
        migrations.CreateModel(
            name='SOA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('mail',
                 models.EmailField(help_text='Email du contact pour la zone',
                                   max_length=254)),
                ('refresh', models.PositiveIntegerField(default=86400,
                                                        help_text='Secondes avant que les DNS secondaires doivent demander le                   serial du DNS primaire pour détecter une modification')),
                ('retry', models.PositiveIntegerField(default=7200,
                                                      help_text='Secondes avant que les DNS secondaires fassent une nouvelle                   demande de serial en cas de timeout du DNS primaire')),
                ('expire', models.PositiveIntegerField(default=3600000,
                                                       help_text='Secondes après lesquelles les DNS secondaires arrêtent de                   de répondre aux requêtes en cas de timeout du DNS primaire')),
                ('ttl', models.PositiveIntegerField(default=172800,
                                                    help_text='Time To Live')),
            ],
            options={
                'permissions': (('view_soa', 'Peut voir un objet soa'),),
            },
        ),
        migrations.AddField(
            model_name='extension',
            name='soa',
            field=models.ForeignKey(default=machines.models.SOA.new_default_soa,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to='machines.SOA'),
        ),
        migrations.CreateModel(
            name='Srv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('service', models.CharField(max_length=31)),
                ('protocole',
                 models.CharField(choices=[('TCP', 'TCP'), ('UDP', 'UDP')],
                                  default='TCP', max_length=3)),
                ('ttl', models.PositiveIntegerField(default=172800,
                                                    help_text='Time To Live')),
                ('priority', models.PositiveIntegerField(default=0,
                                                         help_text="La priorité du serveur cible (valeur entière non négative, plus elle est faible, plus ce serveur sera utilisé s'il est disponible)",
                                                         validators=[
                                                             django.core.validators.MaxValueValidator(
                                                                 65535)])),
                ('weight', models.PositiveIntegerField(default=0,
                                                       help_text='Poids relatif pour les enregistrements de même priorité            (valeur entière de 0 à 65535)',
                                                       validators=[
                                                           django.core.validators.MaxValueValidator(
                                                               65535)])),
                ('port', models.PositiveIntegerField(help_text='Port (tcp/udp)',
                                                     validators=[
                                                         django.core.validators.MaxValueValidator(
                                                             65535)])),
                ('extension',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to='machines.Extension')),
                ('target', models.ForeignKey(help_text='Serveur cible',
                                             on_delete=django.db.models.deletion.PROTECT,
                                             to='machines.Domain')),
            ],
            options={
                'permissions': (('view_soa', 'Peut voir un objet soa'),),
            },
        ),
        migrations.AlterField(
            model_name='extension',
            name='name',
            field=models.CharField(
                help_text='Nom de la zone, doit commencer par un point (.example.org)',
                max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='extension',
            name='origin',
            field=models.OneToOneField(blank=True,
                                       help_text='Enregistrement A associé à la zone',
                                       null=True,
                                       on_delete=django.db.models.deletion.PROTECT,
                                       to='machines.IpList'),
        ),
        migrations.AlterField(
            model_name='extension',
            name='origin_v6',
            field=models.GenericIPAddressField(blank=True,
                                               help_text='Enregistremen AAAA associé à la zone',
                                               null=True, protocol='IPv6'),
        ),
        migrations.AlterField(
            model_name='extension',
            name='origin_v6',
            field=models.GenericIPAddressField(blank=True,
                                               help_text='Enregistrement AAAA associé à la zone',
                                               null=True, protocol='IPv6'),
        ),
        migrations.AlterModelOptions(
            name='domain',
            options={
                'permissions': (('view_domain', 'Peut voir un objet domain'),)},
        ),
        migrations.AlterModelOptions(
            name='extension',
            options={'permissions': (
                ('view_extension', 'Peut voir un objet extension'),
                ('use_all_extension', 'Peut utiliser toutes les extension'))},
        ),
        migrations.AlterModelOptions(
            name='interface',
            options={'permissions': (
                ('view_interface', 'Peut voir un objet interface'), (
                    'change_interface_machine',
                    "Peut changer le propriétaire d'une interface"))},
        ),
        migrations.AlterModelOptions(
            name='iptype',
            options={'permissions': (
                ('view_iptype', 'Peut voir un objet iptype'),
                ('use_all_iptype', 'Peut utiliser tous les iptype'))},
        ),
        migrations.AlterModelOptions(
            name='machinetype',
            options={'permissions': (
                ('view_machinetype', 'Peut voir un objet machinetype'), (
                    'use_all_machinetype',
                    "Peut utiliser n'importe quel type de machine"))},
        ),
        migrations.AlterModelOptions(
            name='ns',
            options={'permissions': (('view_ns', 'Peut voir un objet ns'),)},
        ),
        migrations.AlterModelOptions(
            name='service',
            options={'permissions': (
                ('view_service', 'Peut voir un objet service'),)},
        ),
        migrations.CreateModel(
            name='Ipv6List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('ipv6',
                 models.GenericIPAddressField(protocol='IPv6', unique=True)),
                ('slaac_ip', models.BooleanField(default=False)),
                ('interface',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='machines.Interface')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='ipv6list',
            unique_together=set([('interface', 'slaac_ip')]),
        ),
        migrations.AlterModelOptions(
            name='ipv6list',
            options={'permissions': (
                ('view_ipv6list', 'Peut voir un objet ipv6'), (
                    'change_ipv6list_slaac_ip',
                    'Peut changer la valeur slaac sur une ipv6'))},
        ),
        migrations.AlterUniqueTogether(
            name='ipv6list',
            unique_together=set([]),
        ),
        migrations.AlterField(
            model_name='ipv6list',
            name='interface',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='ipv6list',
                                    to='machines.Interface'),
        ),
        migrations.AlterField(
            model_name='extension',
            name='origin',
            field=models.ForeignKey(blank=True,
                                    help_text='Enregistrement A associé à la zone',
                                    null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='machines.IpList'),
        ),
        migrations.RunPython(
            code=rename_permission_soa_to_srv,
        ),
        migrations.AlterModelOptions(
            name='srv',
            options={'permissions': (('view_srv', 'Peut voir un objet srv'),)},
        ),
        migrations.AlterField(
            model_name='ns',
            name='ns',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    to='machines.Domain'),
        ),
        migrations.AlterField(
            model_name='extension',
            name='soa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to='machines.SOA'),
        ),
        migrations.AlterModelOptions(
            name='service_link',
            options={'permissions': (
                ('view_service_link', 'Peut voir un objet service_link'),)},
        ),
        migrations.RunPython(
            code=remove_permission_text,
        ),
        migrations.RunPython(
            code=remove_permission_alias,
        ),
        migrations.CreateModel(
            name='DName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=255)),
                ('zone',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to='machines.Extension')),
            ],
            options={
                'permissions': (
                    ('view_dname', 'Can view a DNAME record object'),),
                'verbose_name': 'DNAME record',
                'verbose_name_plural': 'DNAME records',
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SshFp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('pub_key_entry',
                 models.TextField(help_text='SSH public key', max_length=2048)),
                ('algo', models.CharField(
                    choices=[('ssh-rsa', 'ssh-rsa'),
                             ('ssh-ed25519', 'ssh-ed25519'),
                             ('ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp256'),
                             ('ecdsa-sha2-nistp384', 'ecdsa-sha2-nistp384'),
                             ('ecdsa-sha2-nistp521', 'ecdsa-sha2-nistp521')],
                    max_length=32)),
                ('comment',
                 models.CharField(blank=True, help_text='Comment',
                                  max_length=255,
                                  null=True)),
                ('machine',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='machines.Machine')),
            ],
            options={
                'verbose_name': 'SSHFP record',
                'verbose_name_plural': 'SSHFP records',
                'permissions': (
                    ('view_sshfp', 'Can view an SSHFP record object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('role_type', models.CharField(max_length=255, unique=True)),
                ('servers', models.ManyToManyField(to='machines.Interface')),
                ('specific_role', models.CharField(blank=True, choices=[
                    ('dhcp-server', 'DHCP server'),
                    ('switch-conf-server', 'Switches configuration server'),
                    ('dns-recursif-server', 'Recursive DNS server'),
                    ('dns-recursive-server', 'Recursive DNS server'),
                    ('ntp-server', 'NTP server'),
                    ('radius-server', 'RADIUS server'),
                    ('log-server', 'Log server'),
                    ('ldap-master-server', 'LDAP master server'),
                    ('ldap-backup-server', 'LDAP backup server'),
                    ('smtp-server', 'SMTP server'),
                    ('postgresql-server', 'postgreSQL server'),
                    ('mysql-server', 'mySQL server'),
                    ('sql-client', 'SQL client'),
                    ('gateway', 'Gateway')], max_length=32, null=True)),
            ],
            options={
                'permissions': (('view_role', 'Can view a role object'),),
                'verbose_name': 'server role',
                'verbose_name_plural': 'server roles',
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.AddField(
            model_name='iptype',
            name='reverse_v4',
            field=models.BooleanField(default=False,
                                      help_text='Activer DNSSEC sur le reverse DNS IPv4'),
        ),
        migrations.AddField(
            model_name='iptype',
            name='reverse_v6',
            field=models.BooleanField(default=False,
                                      help_text='Activer DNSSEC sur le reverse DNS IPv6'),
        ),
        migrations.AddField(
            model_name='iptype',
            name='prefix_v6_length',
            field=models.IntegerField(default=64, validators=[
                django.core.validators.MaxValueValidator(128),
                django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='interface',
            name='mac_address',
            field=macaddress.fields.MACAddressField(integer=False,
                                                    max_length=17),
        ),
        migrations.AlterField(
            model_name='ipv6list',
            name='ipv6',
            field=models.GenericIPAddressField(protocol='IPv6'),
        ),
        migrations.AddField(
            model_name='iptype',
            name='domaine_ip_netmask',
            field=models.IntegerField(default=24,
                                      help_text='Netmask for the ipv4 range domain',
                                      validators=[
                                          django.core.validators.MaxValueValidator(
                                              31),
                                          django.core.validators.MinValueValidator(
                                              8)]),
        ),
        migrations.AddField(
            model_name='iptype',
            name='domaine_ip_network',
            field=models.GenericIPAddressField(blank=True,
                                               help_text='Network containing the ipv4 range domain ip start/stop. Optional',
                                               null=True, protocol='IPv4'),
        ),
        migrations.AlterField(
            model_name='mx',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    to='machines.Domain'),
        ),
        migrations.AlterField(
            model_name='mx',
            name='priority',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterModelOptions(
            name='domain',
            options={
                'permissions': (('view_domain', 'Can view a domain object'),),
                'verbose_name': 'domain', 'verbose_name_plural': 'domains'},
        ),
        migrations.AlterModelOptions(
            name='extension',
            options={'permissions': (
                ('view_extension', 'Can view an extension object'),
                ('use_all_extension', 'Can use all extensions')),
                'verbose_name': 'DNS extension',
                'verbose_name_plural': 'DNS extensions'},
        ),
        migrations.AlterModelOptions(
            name='interface',
            options={'permissions': (
                ('view_interface', 'Can view an interface object'),
                ('change_interface_machine',
                 'Can change the owner of an interface')),
                'verbose_name': 'interface',
                'verbose_name_plural': 'interfaces'},
        ),
        migrations.AlterModelOptions(
            name='iplist',
            options={'permissions': (
                ('view_iplist', 'Can view an IPv4 addresses list object'),),
                'verbose_name': 'IPv4 addresses list',
                'verbose_name_plural': 'IPv4 addresses lists'},
        ),
        migrations.AlterModelOptions(
            name='iptype',
            options={
                'permissions': (('view_iptype', 'Can view an IP type object'),
                                ('use_all_iptype', 'Can use all IP types')),
                'verbose_name': 'IP type', 'verbose_name_plural': 'IP types'},
        ),
        migrations.AlterModelOptions(
            name='ipv6list',
            options={'permissions': (
                ('view_ipv6list', 'Can view an IPv6 addresses list object'), (
                    'change_ipv6list_slaac_ip',
                    'Can change the SLAAC value of an IPv6 addresses list')),
                'verbose_name': 'IPv6 addresses list',
                'verbose_name_plural': 'IPv6 addresses lists'},
        ),
        migrations.AlterModelOptions(
            name='machine',
            options={
                'permissions': (('view_machine', 'Can view a machine object'),
                                ('change_machine_user',
                                 'Can change the user of a machine')),
                'verbose_name': 'machine', 'verbose_name_plural': 'machines'},
        ),
        migrations.AlterModelOptions(
            name='machinetype',
            options={'permissions': (
                ('view_machinetype', 'Can view a machine type object'),
                ('use_all_machinetype', 'Can use all machine types')),
                'verbose_name': 'machine type',
                'verbose_name_plural': 'machine types'},
        ),
        migrations.AlterModelOptions(
            name='mx',
            options={
                'permissions': (('view_mx', 'Can view an MX record object'),),
                'verbose_name': 'MX record',
                'verbose_name_plural': 'MX records'},
        ),
        migrations.AlterModelOptions(
            name='nas',
            options={
                'permissions': (('view_nas', 'Can view a NAS device object'),),
                'verbose_name': 'NAS device',
                'verbose_name_plural': 'NAS devices'},
        ),
        migrations.AlterModelOptions(
            name='ns',
            options={
                'permissions': (('view_ns', 'Can view an NS record object'),),
                'verbose_name': 'NS record',
                'verbose_name_plural': 'NS records'},
        ),
        migrations.AlterModelOptions(
            name='ouvertureport',
            options={'verbose_name': 'ports openings'},
        ),
        migrations.AlterModelOptions(
            name='ouvertureportlist',
            options={'permissions': (
                (
                    'view_ouvertureportlist',
                    'Can view a ports opening list object'),),
                'verbose_name': 'ports opening list',
                'verbose_name_plural': 'ports opening lists'},
        ),
        migrations.AlterModelOptions(
            name='service',
            options={
                'permissions': (('view_service', 'Can view a service object'),),
                'verbose_name': 'service to generate (DHCP, DNS, ...)',
                'verbose_name_plural': 'services to generate (DHCP, DNS, ...)'},
        ),
        migrations.AlterModelOptions(
            name='service_link',
            options={'permissions': (
                (
                    'view_service_link',
                    'Can view a service server link object'),),
                'verbose_name': 'link between service and server',
                'verbose_name_plural': 'links between service and server'},
        ),
        migrations.AlterModelOptions(
            name='soa',
            options={
                'permissions': (('view_soa', 'Can view an SOA record object'),),
                'verbose_name': 'SOA record',
                'verbose_name_plural': 'SOA records'},
        ),
        migrations.AlterModelOptions(
            name='srv',
            options={
                'permissions': (('view_srv', 'Can view an SRV record object'),),
                'verbose_name': 'SRV record',
                'verbose_name_plural': 'SRV records'},
        ),
        migrations.AlterModelOptions(
            name='txt',
            options={
                'permissions': (('view_txt', 'Can view a TXT record object'),),
                'verbose_name': 'TXT record',
                'verbose_name_plural': 'TXT records'},
        ),
        migrations.AlterModelOptions(
            name='vlan',
            options={'permissions': (('view_vlan', 'Can view a VLAN object'),),
                     'verbose_name': 'VLAN', 'verbose_name_plural': 'VLANs'},
        ),
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(
                help_text='Mandatory and unique, must not contain dots.',
                max_length=255),
        ),
        migrations.AlterField(
            model_name='extension',
            name='name',
            field=models.CharField(
                help_text='Zone name, must begin with a dot (.example.org)',
                max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='extension',
            name='origin',
            field=models.ForeignKey(blank=True,
                                    help_text='A record associated with the zone',
                                    null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='machines.IpList'),
        ),
        migrations.AlterField(
            model_name='extension',
            name='origin_v6',
            field=models.GenericIPAddressField(blank=True,
                                               help_text='AAAA record associated with the zone',
                                               null=True, protocol='IPv6'),
        ),
        migrations.AlterField(
            model_name='iptype',
            name='domaine_ip_netmask',
            field=models.IntegerField(default=24,
                                      help_text="Netmask for the domain's IPv4 range",
                                      validators=[
                                          django.core.validators.MaxValueValidator(
                                              31),
                                          django.core.validators.MinValueValidator(
                                              8)]),
        ),
        migrations.AlterField(
            model_name='iptype',
            name='domaine_ip_network',
            field=models.GenericIPAddressField(blank=True,
                                               help_text="Network containing the domain's IPv4 range (optional)",
                                               null=True, protocol='IPv4'),
        ),
        migrations.AlterField(
            model_name='iptype',
            name='reverse_v4',
            field=models.BooleanField(default=False,
                                      help_text='Enable reverse DNS for IPv4'),
        ),
        migrations.AlterField(
            model_name='iptype',
            name='reverse_v6',
            field=models.BooleanField(default=False,
                                      help_text='Enable reverse DNS for IPv6'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='name',
            field=models.CharField(blank=True, help_text='Optional',
                                   max_length=255,
                                   null=True),
        ),
        migrations.AlterField(
            model_name='ouvertureportlist',
            name='name',
            field=models.CharField(help_text='Name of the ports configuration',
                                   max_length=255),
        ),
        migrations.AlterField(
            model_name='service',
            name='min_time_regen',
            field=models.DurationField(default=datetime.timedelta(0, 60),
                                       help_text='Minimal time before regeneration of the service.'),
        ),
        migrations.AlterField(
            model_name='service',
            name='regular_time_regen',
            field=models.DurationField(default=datetime.timedelta(0, 3600),
                                       help_text='Maximal time before regeneration of the service.'),
        ),
        migrations.AlterField(
            model_name='soa',
            name='expire',
            field=models.PositiveIntegerField(default=3600000,
                                              help_text='Seconds before the secondary DNS stop answering requests in case of primary DNS timeout'),
        ),
        migrations.AlterField(
            model_name='soa',
            name='mail',
            field=models.EmailField(
                help_text='Contact email address for the zone',
                max_length=254),
        ),
        migrations.AlterField(
            model_name='soa',
            name='refresh',
            field=models.PositiveIntegerField(default=86400,
                                              help_text='Seconds before the secondary DNS have to ask the primary DNS serial to detect a modification'),
        ),
        migrations.AlterField(
            model_name='soa',
            name='retry',
            field=models.PositiveIntegerField(default=7200,
                                              help_text='Seconds before the secondary DNS ask the serial again in case of a primary DNS timeout'),
        ),
        migrations.AlterField(
            model_name='soa',
            name='ttl',
            field=models.PositiveIntegerField(default=172800,
                                              help_text='Time to Live'),
        ),
        migrations.AlterField(
            model_name='srv',
            name='port',
            field=models.PositiveIntegerField(help_text='TCP/UDP port',
                                              validators=[
                                                  django.core.validators.MaxValueValidator(
                                                      65535)]),
        ),
        migrations.AlterField(
            model_name='srv',
            name='priority',
            field=models.PositiveIntegerField(default=0,
                                              help_text='Priority of the target server (positive integer value, the lower it is, the more the server will be used if available)',
                                              validators=[
                                                  django.core.validators.MaxValueValidator(
                                                      65535)]),
        ),
        migrations.AlterField(
            model_name='srv',
            name='target',
            field=models.ForeignKey(help_text='Target server',
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='machines.Domain'),
        ),
        migrations.AlterField(
            model_name='srv',
            name='ttl',
            field=models.PositiveIntegerField(default=172800,
                                              help_text='Time to Live'),
        ),
        migrations.AlterField(
            model_name='srv',
            name='weight',
            field=models.PositiveIntegerField(default=0,
                                              help_text='Relative weight for records with the same priority (integer value between 0 and 65535)',
                                              validators=[
                                                  django.core.validators.MaxValueValidator(
                                                      65535)]),
        ),
        migrations.AddField(
            model_name='vlan',
            name='arp_protect',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vlan',
            name='dhcp_snooping',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vlan',
            name='dhcpv6_snooping',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vlan',
            name='igmp',
            field=models.BooleanField(default=False,
                                      help_text='Gestion multicast v4'),
        ),
        migrations.AddField(
            model_name='vlan',
            name='mld',
            field=models.BooleanField(default=False,
                                      help_text='Gestion multicast v6'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='extension',
            name='dnssec',
            field=models.BooleanField(default=False,
                                      help_text='Should the zone be signed with DNSSEC'),
        ),
        migrations.RunPython(
            code=migrate,
        ),
        migrations.AlterField(
            model_name='role',
            name='specific_role',
            field=models.CharField(blank=True,
                                   choices=[('dhcp-server', 'DHCP server'), (
                                       'switch-conf-server',
                                       'Switches configuration server'), (
                                                'dns-recursive-server',
                                                'Recursive DNS server'),
                                            ('ntp-server', 'NTP server'),
                                            ('radius-server', 'RADIUS server'),
                                            ('log-server', 'Log server'), (
                                                'ldap-master-server',
                                                'LDAP master server'), (
                                                'ldap-backup-server',
                                                'LDAP backup server'),
                                            ('smtp-server', 'SMTP server'), (
                                                'postgresql-server',
                                                'postgreSQL server'),
                                            ('mysql-server', 'mySQL server'),
                                            ('sql-client', 'SQL client'),
                                            ('gateway', 'Gateway')],
                                   max_length=32,
                                   null=True),
        ),
        migrations.AlterModelOptions(
            name='ouvertureport',
            options={'verbose_name': 'ports opening',
                     'verbose_name_plural': 'ports openings'},
        ),
        migrations.AlterField(
            model_name='nas',
            name='port_access_mode',
            field=models.CharField(
                choices=[('802.1X', '802.1X'), ('Mac-address', 'MAC-address')],
                default='802.1X', max_length=32),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='igmp',
            field=models.BooleanField(default=False,
                                      help_text='v4 multicast management'),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='mld',
            field=models.BooleanField(default=False,
                                      help_text='v6 multicast management'),
        ),
        migrations.RenameField(
            model_name='interface',
            old_name='type',
            new_name='machine_type',
        ),
        migrations.RenameField(
            model_name='iptype',
            old_name='type',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='machinetype',
            old_name='type',
            new_name='name',
        ),
    ]
