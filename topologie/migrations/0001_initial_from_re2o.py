# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2019  Alexandre Iooss

from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models

import re2o.mixins


def transfer_bornes(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    machinetype = apps.get_model("machines", "MachineType")
    borne = apps.get_model("topologie", "Borne")
    interface = apps.get_model("machines", "Interface")
    bornes_list = machinetype.objects.using(db_alias).filter(
        type__icontains='borne')
    if bornes_list:
        for inter in interface.objects.using(db_alias).filter(
                type=bornes_list.first()):
            borne_object = borne()
            borne_object.interface_ptr_id = inter.pk
            borne_object.__dict__.update(inter.__dict__)
            borne_object.save()


def untransfer_bornes(apps, schema_editor):
    return


def transfer_sw(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    newswitch = apps.get_model("topologie", "NewSwitch")
    switch = apps.get_model("topologie", "Switch")
    interface = apps.get_model("machines", "Interface")
    sw_list = switch.objects.using(db_alias).all()
    for sw in sw_list:
        new_sw = newswitch()
        new_sw.location = sw.location
        new_sw.number = sw.number
        new_sw.details = sw.details
        new_sw.stack = sw.stack
        new_sw.stack_member_id = sw.stack_member_id
        new_sw.model = sw.model
        new_sw.interface_ptr_id = sw.switch_interface.pk
        new_sw.__dict__.update(sw.switch_interface.__dict__)
        new_sw.save()


def untransfer_sw(apps, schema_editor):
    return


def transfer_port(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    port = apps.get_model("topologie", "Port")
    switch = apps.get_model("topologie", "NewSwitch")
    port_list = port.objects.using(db_alias).all()
    for p in port_list:
        p.new_switch = switch.objects.filter(
            interface_ptr=p.switch.switch_interface).first()
        p.save()


def untransfer_port(apps, schema_editor):
    return


def transfer_ap(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    ap = apps.get_model("topologie", "AccessPoint")
    new_ap = apps.get_model("topologie", "NewAccessPoint")
    ap_list = ap.objects.using(db_alias).all()
    for borne in ap_list:
        new_borne = new_ap()
        new_borne.machine_ptr_id = borne.machine.pk
        new_borne.__dict__.update(borne.machine.__dict__)
        new_borne.location = borne.location
        new_borne.save()


def untransfer_ap(apps, schema_editor):
    return


def transfer_sw2(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    newswitch = apps.get_model("topologie", "NewSw")
    switch = apps.get_model("topologie", "Switch")
    machine = apps.get_model("machines", "Machine")
    sw_list = switch.objects.using(db_alias).all()
    for sw in sw_list:
        new_sw = newswitch()
        new_sw.location = sw.location
        new_sw.number = sw.number
        new_sw.details = sw.details
        new_sw.stack = sw.stack
        new_sw.stack_member_id = sw.stack_member_id
        new_sw.model = sw.model
        new_sw.machine_ptr_id = sw.interface_ptr.machine.pk
        new_sw.__dict__.update(sw.interface_ptr.machine.__dict__)
        new_sw.save()


def untransfer_sw2(apps, schema_editor):
    return


def transfer_port2(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    port = apps.get_model("topologie", "Port")
    switch = apps.get_model("topologie", "NewSw")
    port_list = port.objects.using(db_alias).all()
    for p in port_list:
        p.new_sw = switch.objects.filter(machine_ptr=p.switch.machine).first()
        p.save()


def untransfer_port2(apps, schema_editor):
    return


def transfer_profil(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    port = apps.get_model("topologie", "Port")
    profil = apps.get_model("topologie", "PortProfile")
    vlan = apps.get_model("machines", "Vlan")
    port_list = port.objects.using(db_alias).all()
    profil_nothing = profil.objects.using(db_alias).create(name='nothing',
                                                           profil_default='nothing',
                                                           radius_type='NO')
    profil_uplink = profil.objects.using(db_alias).create(name='uplink',
                                                          profil_default='uplink',
                                                          radius_type='NO')
    profil_machine = profil.objects.using(db_alias).create(name='asso_machine',
                                                           profil_default='asso_machine',
                                                           radius_type='NO')
    profil_room = profil.objects.using(db_alias).create(name='room',
                                                        profil_default='room',
                                                        radius_type='NO')
    profil_borne = profil.objects.using(db_alias).create(name='accesspoint',
                                                         profil_default='accesspoint',
                                                         radius_type='NO')
    for vlan_instance in vlan.objects.using(db_alias).all():
        if port.objects.using(db_alias).filter(vlan_force=vlan_instance):
            custom_profile = profil.objects.using(db_alias).create(
                name='vlan-force-' + str(vlan_instance.vlan_id),
                radius_type='NO', vlan_untagged=vlan_instance)
            port.objects.using(db_alias).filter(
                vlan_force=vlan_instance).update(custom_profile=custom_profile)
    if port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius='STRICT').count() > port.objects.using(db_alias).filter(
        room__isnull=False).filter(
        radius='NO').count() and port.objects.using(db_alias).filter(
        room__isnull=False).filter(
        radius='STRICT').count() > port.objects.using(db_alias).filter(
        room__isnull=False).filter(radius='COMMON').count():
        profil_room.radius_type = 'MAC-radius'
        profil_room.radius_mode = 'STRICT'
        common_profil = profil.objects.using(db_alias).create(
            name='mac-radius-common', radius_type='MAC-radius',
            radius_mode='COMMON')
        no_rad_profil = profil.objects.using(db_alias).create(name='no-radius',
                                                              radius_type='NO')
        port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius='COMMON').update(custom_profile=common_profil)
        port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius='NO').update(custom_profile=no_rad_profil)
    elif port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius='COMMON').count() > port.objects.using(db_alias).filter(
        room__isnull=False).filter(
        radius='NO').count() and port.objects.using(db_alias).filter(
        room__isnull=False).filter(
        radius='COMMON').count() > port.objects.using(db_alias).filter(
        room__isnull=False).filter(radius='STRICT').count():
        profil_room.radius_type = 'MAC-radius'
        profil_room.radius_mode = 'COMMON'
        strict_profil = profil.objects.using(db_alias).create(
            name='mac-radius-strict', radius_type='MAC-radius',
            radius_mode='STRICT')
        no_rad_profil = profil.objects.using(db_alias).create(name='no-radius',
                                                              radius_type='NO')
        port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius='STRICT').update(custom_profile=strict_profil)
        port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius='NO').update(custom_profile=no_rad_profil)
    else:
        strict_profil = profil.objects.using(db_alias).create(
            name='mac-radius-strict', radius_type='MAC-radius',
            radius_mode='STRICT')
        common_profil = profil.objects.using(db_alias).create(
            name='mac-radius-common', radius_type='MAC-radius',
            radius_mode='COMMON')
        port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius='STRICT').update(custom_profile=strict_profil)
        port.objects.using(db_alias).filter(room__isnull=False).filter(
            radius='NO').update(custom_profile=common_profil)
    profil_room.save()


def create_dormitory(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    dormitory = apps.get_model("topologie", "Dormitory")
    building = apps.get_model("topologie", "Building")
    dorm = dormitory.objects.using(db_alias).create(name="Residence")
    building.objects.using(db_alias).update(dormitory=dorm)


def delete_dormitory(apps, schema_editor):
    pass


def transfer_room(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    room_obj = apps.get_model("topologie", "Room")
    building_obj = apps.get_model("topologie", "Building")
    dorm_obj = apps.get_model("topologie", "Dormitory")
    dorm = dorm_obj.objects.using(db_alias).first()
    for room in room_obj.objects.using(db_alias).all():
        building, created = building_obj.objects.using(db_alias).get_or_create(
            name=room.name[0].upper(), dormitory=dorm)
        room.building = building
        room.name = room.name[1:]
        room.save()


def untransfer_room(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    replaces = [('topologie', '0001_initial'),
                ('topologie', '0002_auto_20160703_1118'),
                ('topologie', '0003_room'),
                ('topologie', '0004_auto_20160703_1122'),
                ('topologie', '0005_auto_20160703_1123'),
                ('topologie', '0006_auto_20160703_1129'),
                ('topologie', '0007_auto_20160703_1148'),
                ('topologie', '0008_port_room'),
                ('topologie', '0009_auto_20160703_1200'),
                ('topologie', '0010_auto_20160704_2148'),
                ('topologie', '0011_auto_20160704_2153'),
                ('topologie', '0012_port_machine_interface'),
                ('topologie', '0013_port_related'),
                ('topologie', '0014_auto_20160706_1238'),
                ('topologie', '0015_auto_20160706_1452'),
                ('topologie', '0016_auto_20160706_1531'),
                ('topologie', '0017_auto_20160718_1141'),
                ('topologie', '0018_room_details'),
                ('topologie', '0019_auto_20161026_1348'),
                ('topologie', '0020_auto_20161119_0033'),
                ('topologie', '0021_port_radius'),
                ('topologie', '0022_auto_20161211_1622'),
                ('topologie', '0023_auto_20170826_1530'),
                ('topologie', '0024_auto_20170826_1800'),
                ('topologie', '0023_auto_20170817_1654'),
                ('topologie', '0024_auto_20170818_1021'),
                ('topologie', '0025_merge_20170902_1242'),
                ('topologie', '0026_auto_20170902_1245'),
                ('topologie', '0027_auto_20170905_1442'),
                ('topologie', '0028_auto_20170913_1503'),
                ('topologie', '0029_auto_20171002_0334'),
                ('topologie', '0030_auto_20171004_0235'),
                ('topologie', '0031_auto_20171015_2033'),
                ('topologie', '0032_auto_20171026_0338'),
                ('topologie', '0033_auto_20171231_1743'),
                ('topologie', '0034_borne'),
                ('topologie', '0035_auto_20180324_0023'),
                ('topologie', '0036_transferborne'),
                ('topologie', '0037_auto_20180325_0127'),
                ('topologie', '0038_transfersw'),
                ('topologie', '0039_port_new_switch'),
                ('topologie', '0040_transferports'),
                ('topologie', '0041_transferportsw'),
                ('topologie', '0042_transferswitch'),
                ('topologie', '0043_renamenewswitch'),
                ('topologie', '0044_auto_20180326_0002'),
                ('topologie', '0045_auto_20180326_0123'),
                ('topologie', '0046_auto_20180326_0129'),
                ('topologie', '0047_ap_machine'),
                ('topologie', '0048_ap_machine'),
                ('topologie', '0049_switchs_machine'),
                ('topologie', '0050_port_new_switch'),
                ('topologie', '0051_switchs_machine'),
                ('topologie', '0052_transferports'),
                ('topologie', '0053_finalsw'),
                ('topologie', '0054_auto_20180326_1742'),
                ('topologie', '0055_auto_20180329_0431'),
                ('topologie', '0056_building_switchbay'),
                ('topologie', '0057_auto_20180408_0316'),
                ('topologie', '0058_remove_switch_location'),
                ('topologie', '0059_auto_20180415_2249'),
                ('topologie', '0060_server'), ('topologie', '0061_portprofile'),
                ('topologie', '0062_auto_20180815_1918'),
                ('topologie', '0063_auto_20180919_2225'),
                ('topologie', '0064_switch_automatic_provision'),
                ('topologie', '0065_auto_20180927_1836'),
                ('topologie', '0066_modelswitch_commercial_name'),
                ('topologie', '0067_auto_20181230_1819'),
                ('topologie', '0068_auto_20190102_1758'),
                ('topologie', '0069_auto_20190108_1439'),
                ('topologie', '0070_auto_20190218_1743'),
                ('topologie', '0071_auto_20190218_1936')]

    dependencies = [
        ('machines', '0049_vlan'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('preferences', '0051_auto_20180919_2225'),
        ('machines', '0076_auto_20180130_1623'),
        ('machines', '0026_auto_20161026_1348'),
        ('machines', '0082_auto_20180525_2209'),
        ('machines', '0014_auto_20160706_1220'),
        ('machines', '0081_auto_20180521_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='Switch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('building', models.CharField(max_length=10)),
                ('number', models.IntegerField()),
                ('details', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('port', models.IntegerField()),
                ('details', models.CharField(blank=True, max_length=255)),
                ('switch',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   related_name='ports',
                                   to='topologie.Switch')),
                ('room', models.ForeignKey(blank=True, null=True,
                                           on_delete=django.db.models.deletion.PROTECT,
                                           to='topologie.Room')),
                ('machine_interface', models.ForeignKey(blank=True, null=True,
                                                        on_delete=django.db.models.deletion.SET_NULL,
                                                        to='machines.Interface')),
                ('related', models.OneToOneField(blank=True, null=True,
                                                 on_delete=django.db.models.deletion.CASCADE,
                                                 related_name='related_port',
                                                 to='topologie.Port')),
                ('radius', models.CharField(
                    choices=[('NO', 'NO'), ('STRICT', 'STRICT'),
                             ('BLOQ', 'BLOQ'), ('COMMON', 'COMMON')],
                    default='NO', max_length=32)),
                ('vlan_force', models.ForeignKey(blank=True, null=True,
                                                 on_delete=django.db.models.deletion.SET_NULL,
                                                 to='machines.Vlan')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='port',
            unique_together=set([('switch', 'port')]),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('details', models.CharField(blank=True, max_length=255)),
                ('building', models.CharField(max_length=255, unique=True)),
                ('number', models.IntegerField()),
                ('room', models.IntegerField(default=1)),
            ],
        ),
        migrations.AddField(
            model_name='switch',
            name='location',
            field=models.CharField(default='test', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='switch',
            name='switch_interface',
            field=models.OneToOneField(default=1,
                                       on_delete=django.db.models.deletion.CASCADE,
                                       to='machines.Interface'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='switch',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set([('building', 'number')]),
        ),
        migrations.AlterField(
            model_name='room',
            name='building',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='room',
            name='number',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set([('building', 'room', 'number')]),
        ),
        migrations.AlterField(
            model_name='room',
            name='number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.RenameField(
            model_name='room',
            old_name='building',
            new_name='name',
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='room',
            name='details',
        ),
        migrations.RemoveField(
            model_name='room',
            name='number',
        ),
        migrations.RemoveField(
            model_name='room',
            name='room',
        ),
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AddField(
            model_name='room',
            name='details',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.RemoveField(
            model_name='switch',
            name='building',
        ),
        migrations.CreateModel(
            name='Stack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                (
                    'name',
                    models.CharField(blank=True, max_length=32, null=True)),
                ('stack_id', models.CharField(max_length=32, unique=True)),
                ('details',
                 models.CharField(blank=True, max_length=255, null=True)),
                ('member_id_min', models.PositiveIntegerField()),
                ('member_id_max', models.PositiveIntegerField()),
            ],
            options={
                'permissions': (('view_stack', 'Peut voir un objet stack'),),
            },
        ),
        migrations.AddField(
            model_name='switch',
            name='stack_member_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='switch',
            name='stack',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to='topologie.Stack'),
        ),
        migrations.AlterUniqueTogether(
            name='switch',
            unique_together=set([('stack', 'stack_member_id')]),
        ),
        migrations.AlterField(
            model_name='switch',
            name='stack',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    to='topologie.Stack'),
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['name'], 'permissions': (
                ('view_room', 'Peut voir un objet chambre'),)},
        ),
        migrations.AlterField(
            model_name='port',
            name='port',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='switch',
            name='number',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='switch',
            name='stack_member_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='ConstructorSwitch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ModelSwitch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=255)),
                ('constructor',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to='topologie.ConstructorSwitch')),
            ],
            options={
                'permissions': (
                    ('view_modelswitch', 'Peut voir un objet modelswitch'),),
            },
        ),
        migrations.AddField(
            model_name='switch',
            name='model',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    to='topologie.ModelSwitch'),
        ),
        migrations.AlterModelOptions(
            name='constructorswitch',
            options={'permissions': (('view_constructorswitch',
                                      'Peut voir un objet constructorswitch'),)},
        ),
        migrations.AlterModelOptions(
            name='port',
            options={
                'permissions': (('view_port', 'Peut voir un objet port'),)},
        ),
        migrations.AlterModelOptions(
            name='switch',
            options={
                'permissions': (('view_switch', 'Peut voir un objet switch'),)},
        ),
        migrations.CreateModel(
            name='Borne',
            fields=[
                ('interface_ptr', models.OneToOneField(auto_created=True,
                                                       on_delete=django.db.models.deletion.CASCADE,
                                                       parent_link=True,
                                                       primary_key=True,
                                                       serialize=False,
                                                       to='machines.Interface')),
                ('location', models.CharField(blank=True,
                                              help_text="Détails sur la localisation de l'AP",
                                              max_length=255, null=True)),
            ],
            options={
                'permissions': (('view_borne', 'Peut voir une borne'),),
            },
            bases=('machines.interface',),
        ),
        migrations.RunPython(
            code=transfer_bornes,
            reverse_code=untransfer_bornes,
        ),
        migrations.CreateModel(
            name='NewSwitch',
            fields=[
                ('interface_ptr', models.OneToOneField(auto_created=True,
                                                       on_delete=django.db.models.deletion.CASCADE,
                                                       parent_link=True,
                                                       primary_key=True,
                                                       serialize=False,
                                                       to='machines.Interface')),
                ('location', models.CharField(max_length=255)),
                ('number', models.PositiveIntegerField()),
                ('stack_member_id',
                 models.PositiveIntegerField(blank=True, null=True)),
                ('model', models.ForeignKey(blank=True, null=True,
                                            on_delete=django.db.models.deletion.SET_NULL,
                                            to='topologie.ModelSwitch')),
                ('stack', models.ForeignKey(blank=True, null=True,
                                            on_delete=django.db.models.deletion.SET_NULL,
                                            to='topologie.Stack')),
            ],
            bases=('machines.interface',),
        ),
        migrations.AlterUniqueTogether(
            name='newswitch',
            unique_together=set([('stack', 'stack_member_id')]),
        ),
        migrations.RunPython(
            code=transfer_sw,
            reverse_code=untransfer_sw,
        ),
        migrations.AddField(
            model_name='port',
            name='new_switch',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='ports',
                                    to='topologie.NewSwitch'),
        ),
        migrations.RunPython(
            code=transfer_port,
            reverse_code=untransfer_port,
        ),
        migrations.AlterUniqueTogether(
            name='port',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='port',
            name='switch',
        ),
        migrations.RenameField(
            model_name='Port',
            old_name='new_switch',
            new_name='switch',
        ),
        migrations.DeleteModel(
            name='Switch',
        ),
        migrations.RenameModel(
            old_name='NewSwitch',
            new_name='Switch',
        ),
        migrations.RenameModel(
            old_name='Borne',
            new_name='AccessPoint',
        ),
        migrations.AlterModelOptions(
            name='accesspoint',
            options={'permissions': (('view_ap', 'Peut voir une borne'),)},
        ),
        migrations.AlterModelOptions(
            name='switch',
            options={
                'permissions': (('view_switch', 'Peut voir un objet switch'),)},
        ),
        migrations.AlterField(
            model_name='port',
            name='switch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='ports',
                                    to='topologie.Switch'),
        ),
        migrations.AlterUniqueTogether(
            name='port',
            unique_together=set([('switch', 'port')]),
        ),
        migrations.CreateModel(
            name='NewAccessPoint',
            fields=[
                ('machine_ptr', models.OneToOneField(auto_created=True,
                                                     on_delete=django.db.models.deletion.CASCADE,
                                                     parent_link=True,
                                                     primary_key=True,
                                                     serialize=False,
                                                     to='machines.Machine')),
                ('location', models.CharField(blank=True,
                                              help_text="Détails sur la localisation de l'AP",
                                              max_length=255, null=True)),
            ],
            bases=('machines.machine',),
        ),
        migrations.RunPython(
            code=transfer_ap,
            reverse_code=untransfer_ap,
        ),
        migrations.DeleteModel(
            name='AccessPoint',
        ),
        migrations.RenameModel(
            old_name='NewAccessPoint',
            new_name='AccessPoint',
        ),
        migrations.CreateModel(
            name='NewSw',
            fields=[
                ('machine_ptr', models.OneToOneField(auto_created=True,
                                                     on_delete=django.db.models.deletion.CASCADE,
                                                     parent_link=True,
                                                     primary_key=True,
                                                     serialize=False,
                                                     to='machines.Machine')),
                ('location', models.CharField(max_length=255)),
                ('number', models.PositiveIntegerField()),
                ('stack_member_id',
                 models.PositiveIntegerField(blank=True, null=True)),
                ('model', models.ForeignKey(blank=True, null=True,
                                            on_delete=django.db.models.deletion.SET_NULL,
                                            to='topologie.ModelSwitch')),
                ('stack', models.ForeignKey(blank=True, null=True,
                                            on_delete=django.db.models.deletion.SET_NULL,
                                            to='topologie.Stack')),
            ],
            bases=('machines.machine',),
        ),
        migrations.AddField(
            model_name='port',
            name='new_sw',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='ports', to='topologie.NewSw'),
        ),
        migrations.RunPython(
            code=transfer_sw2,
            reverse_code=untransfer_sw2,
        ),
        migrations.AlterUniqueTogether(
            name='port',
            unique_together=set([]),
        ),
        migrations.RunPython(
            code=transfer_port2,
            reverse_code=untransfer_port2,
        ),
        migrations.RemoveField(
            model_name='port',
            name='switch',
        ),
        migrations.RenameField(
            model_name='Port',
            old_name='new_sw',
            new_name='switch',
        ),
        migrations.DeleteModel(
            name='Switch',
        ),
        migrations.RenameModel(
            old_name='NewSw',
            new_name='Switch',
        ),
        migrations.AlterModelOptions(
            name='accesspoint',
            options={
                'permissions': (('view_accesspoint', 'Peut voir une borne'),)},
        ),
        migrations.AlterModelOptions(
            name='switch',
            options={
                'permissions': (('view_switch', 'Peut voir un objet switch'),)},
        ),
        migrations.AlterField(
            model_name='port',
            name='switch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='ports',
                                    to='topologie.Switch'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='port',
            name='custom_profile',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='topologie.PortProfile'),
        ),
        migrations.AlterUniqueTogether(
            name='port',
            unique_together=set([('switch', 'port')]),
        ),
        migrations.AddField(
            model_name='switch',
            name='switchbay',
            field=models.ForeignKey(blank=True,
                                    help_text='Baie de brassage du switch',
                                    null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    to='topologie.SwitchBay'),
        ),
        migrations.RemoveField(
            model_name='switch',
            name='location',
        ),
        migrations.AlterField(
            model_name='switch',
            name='model',
            field=models.ForeignKey(blank=True, help_text='Modèle du switch',
                                    null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    to='topologie.ModelSwitch'),
        ),
        migrations.AlterField(
            model_name='switch',
            name='number',
            field=models.PositiveIntegerField(help_text='Nombre de ports'),
        ),
        migrations.AlterUniqueTogether(
            name='switch',
            unique_together=set([('stack', 'stack_member_id')]),
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'permissions': (
                    ('view_building', 'Peut voir un objet batiment'),),
            },
            bases=(re2o.mixins.AclMixin, re2o.mixins.RevMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SwitchBay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('info', models.CharField(blank=True,
                                          help_text='Informations particulières',
                                          max_length=255, null=True)),
                ('building',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                   to='topologie.Building')),
            ],
            options={
                'permissions': (
                    ('view_switchbay', 'Peut voir un objet baie de brassage'),),
            },
            bases=(re2o.mixins.AclMixin, re2o.mixins.RevMixin, models.Model),
        ),
        migrations.AlterField(
            model_name='switch',
            name='stack_member_id',
            field=models.PositiveIntegerField(blank=True,
                                              help_text='Baie de brassage du switch',
                                              null=True),
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('machines.machine',),
        ),
        migrations.CreateModel(
            name='PortProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('profil_default', models.CharField(blank=True,
                                                    choices=[('room', 'room'), (
                                                        'accespoint',
                                                        'accesspoint'),
                                                             ('uplink',
                                                              'uplink'),
                                                             ('asso_machine',
                                                              'asso_machine'), (
                                                                 'nothing',
                                                                 'nothing')],
                                                    max_length=32, null=True,
                                                    unique=True,
                                                    verbose_name='profil default')),
                ('radius_type', models.CharField(
                    choices=[('NO', 'NO'), ('802.1X', '802.1X'),
                             ('MAC-radius', 'MAC-radius')],
                    help_text='Type of radius auth : inactive, mac-address or 802.1X',
                    max_length=32, verbose_name='RADIUS type')),
                ('radius_mode', models.CharField(
                    choices=[('STRICT', 'STRICT'), ('COMMON', 'COMMON')],
                    default='COMMON',
                    help_text='In case of mac-auth : mode common or strict on this port',
                    max_length=32, verbose_name='RADIUS mode')),
                ('speed', models.CharField(
                    choices=[('10-half', '10-half'), ('100-half', '100-half'),
                             ('10-full', '10-full'), ('100-full', '100-full'),
                             ('1000-full', '1000-full'), ('auto', 'auto'),
                             ('auto-10', 'auto-10'), ('auto-100', 'auto-100')],
                    default='auto', help_text='Port speed limit', max_length=32,
                    verbose_name='Speed')),
                ('mac_limit', models.IntegerField(blank=True,
                                                  help_text='Limit of mac-address on this port',
                                                  null=True,
                                                  verbose_name='Mac limit')),
                ('flow_control',
                 models.BooleanField(default=False, help_text='Flow control',
                                     verbose_name='Flow control')),
                ('dhcp_snooping', models.BooleanField(default=False,
                                                      help_text='Protect against rogue dhcp',
                                                      verbose_name='Dhcp snooping')),
                ('dhcpv6_snooping', models.BooleanField(default=False,
                                                        help_text='Protect against rogue dhcpv6',
                                                        verbose_name='Dhcpv6 snooping')),
                ('arp_protect', models.BooleanField(default=False,
                                                    help_text='Check if ip is dhcp assigned',
                                                    verbose_name='Arp protect')),
                ('ra_guard', models.BooleanField(default=False,
                                                 help_text='Protect against rogue ra',
                                                 verbose_name='Ra guard')),
                ('loop_protect', models.BooleanField(default=False,
                                                     help_text='Protect again loop',
                                                     verbose_name='Loop Protect')),
                ('vlan_tagged',
                 models.ManyToManyField(blank=True, related_name='vlan_tagged',
                                        to='machines.Vlan',
                                        verbose_name='VLAN(s) tagged')),
                ('vlan_untagged', models.ForeignKey(blank=True, null=True,
                                                    on_delete=django.db.models.deletion.SET_NULL,
                                                    related_name='vlan_untagged',
                                                    to='machines.Vlan',
                                                    verbose_name='VLAN untagged')),
            ],
            options={
                'verbose_name': 'Port profile',
                'permissions': (
                    ('view_port_profile', 'Can view a port profile object'),),
                'verbose_name_plural': 'Port profiles',
            },
            bases=(re2o.mixins.AclMixin, re2o.mixins.RevMixin, models.Model),
        ),
        migrations.RunPython(
            code=transfer_profil,
        ),
        migrations.RemoveField(
            model_name='port',
            name='radius',
        ),
        migrations.RemoveField(
            model_name='port',
            name='vlan_force',
        ),
        migrations.AddField(
            model_name='port',
            name='state',
            field=models.BooleanField(default=True,
                                      help_text='Port state Active',
                                      verbose_name='Port State Active'),
        ),
        migrations.AlterModelOptions(
            name='accesspoint',
            options={'permissions': (
                ('view_accesspoint', 'Can view an access point object'),),
                'verbose_name': 'access point',
                'verbose_name_plural': 'access points'},
        ),
        migrations.AlterModelOptions(
            name='building',
            options={'permissions': (
                ('view_building', 'Can view a building object'),),
                'verbose_name': 'building',
                'verbose_name_plural': 'buildings'},
        ),
        migrations.AlterModelOptions(
            name='constructorswitch',
            options={'permissions': (('view_constructorswitch',
                                      'Can view a switch constructor object'),),
                     'verbose_name': 'switch constructor',
                     'verbose_name_plural': 'switch constructors'},
        ),
        migrations.AlterModelOptions(
            name='modelswitch',
            options={'permissions': (
                ('view_modelswitch', 'Can view a switch model object'),),
                'verbose_name': 'switch model',
                'verbose_name_plural': 'switch models'},
        ),
        migrations.AlterModelOptions(
            name='port',
            options={'permissions': (('view_port', 'Can view a port object'),),
                     'verbose_name': 'port', 'verbose_name_plural': 'ports'},
        ),
        migrations.AlterModelOptions(
            name='portprofile',
            options={'permissions': (
                ('view_port_profile', 'Can view a port profile object'),),
                'verbose_name': 'port profile',
                'verbose_name_plural': 'port profiles'},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['name'],
                     'permissions': (('view_room', 'Can view a room object'),),
                     'verbose_name': 'room', 'verbose_name_plural': 'rooms'},
        ),
        migrations.AlterModelOptions(
            name='stack',
            options={
                'permissions': (('view_stack', 'Can view a stack object'),),
                'verbose_name': 'switches stack',
                'verbose_name_plural': 'switches stacks'},
        ),
        migrations.AlterModelOptions(
            name='switch',
            options={
                'permissions': (('view_switch', 'Can view a switch object'),),
                'verbose_name': 'switch', 'verbose_name_plural': 'switches'},
        ),
        migrations.AlterModelOptions(
            name='switchbay',
            options={'permissions': (
                ('view_switchbay', 'Can view a switch bay object'),),
                'verbose_name': 'switch bay',
                'verbose_name_plural': 'switch bays'},
        ),
        migrations.AlterField(
            model_name='accesspoint',
            name='location',
            field=models.CharField(blank=True,
                                   help_text="Details about the AP's location",
                                   max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='port',
            name='state',
            field=models.BooleanField(default=True,
                                      help_text='Port state Active',
                                      verbose_name='Port state Active'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='arp_protect',
            field=models.BooleanField(default=False,
                                      help_text='Check if IP adress is DHCP assigned',
                                      verbose_name='ARP protection'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='dhcp_snooping',
            field=models.BooleanField(default=False,
                                      help_text='Protect against rogue DHCP',
                                      verbose_name='DHCP snooping'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='dhcpv6_snooping',
            field=models.BooleanField(default=False,
                                      help_text='Protect against rogue DHCPv6',
                                      verbose_name='DHCPv6 snooping'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='flow_control',
            field=models.BooleanField(default=False, help_text='Flow control'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='loop_protect',
            field=models.BooleanField(default=False,
                                      help_text='Protect against loop',
                                      verbose_name='Loop protection'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='mac_limit',
            field=models.IntegerField(blank=True,
                                      help_text='Limit of MAC-address on this port',
                                      null=True, verbose_name='MAC limit'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='profil_default',
            field=models.CharField(blank=True, choices=[('room', 'room'), (
                'accespoint', 'accesspoint'), ('uplink', 'uplink'),
                                                        ('asso_machine',
                                                         'asso_machine'),
                                                        ('nothing', 'nothing')],
                                   max_length=32, null=True, unique=True,
                                   verbose_name='Default profile'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='ra_guard',
            field=models.BooleanField(default=False,
                                      help_text='Protect against rogue RA',
                                      verbose_name='RA guard'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='radius_mode',
            field=models.CharField(
                choices=[('STRICT', 'STRICT'), ('COMMON', 'COMMON')],
                default='COMMON',
                help_text='In case of MAC-authentication : mode COMMON or STRICT on this port',
                max_length=32, verbose_name='RADIUS mode'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='radius_type',
            field=models.CharField(choices=[('NO', 'NO'), ('802.1X', '802.1X'),
                                            ('MAC-radius', 'MAC-radius')],
                                   help_text='Type of RADIUS authentication : inactive, MAC-address or 802.1X',
                                   max_length=32, verbose_name='RADIUS type'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='speed',
            field=models.CharField(
                choices=[('10-half', '10-half'), ('100-half', '100-half'),
                         ('10-full', '10-full'), ('100-full', '100-full'),
                         ('1000-full', '1000-full'), ('auto', 'auto'),
                         ('auto-10', 'auto-10'), ('auto-100', 'auto-100')],
                default='auto', help_text='Port speed limit', max_length=32),
        ),
        migrations.AlterField(
            model_name='switch',
            name='model',
            field=models.ForeignKey(blank=True, help_text='Switch model',
                                    null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    to='topologie.ModelSwitch'),
        ),
        migrations.AlterField(
            model_name='switch',
            name='number',
            field=models.PositiveIntegerField(help_text='Number of ports'),
        ),
        migrations.AlterField(
            model_name='switch',
            name='stack_member_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='switch',
            name='switchbay',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.SET_NULL,
                                    to='topologie.SwitchBay'),
        ),
        migrations.AlterField(
            model_name='switchbay',
            name='info',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='modelswitch',
            name='firmware',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='switch',
            name='management_creds',
            field=models.ForeignKey(blank=True,
                                    help_text='Management credentials for the switch',
                                    null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='preferences.SwitchManagementCred'),
        ),
        migrations.AddField(
            model_name='switch',
            name='radius_key',
            field=models.ForeignKey(blank=True,
                                    help_text='RADIUS key of the switch',
                                    null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='preferences.RadiusKey'),
        ),
        migrations.AddField(
            model_name='switch',
            name='automatic_provision',
            field=models.BooleanField(default=False,
                                      help_text='Automatic provision for the switch'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='profil_default',
            field=models.CharField(blank=True, choices=[('room', 'room'), (
                'access_point', 'access_point'), ('uplink', 'uplink'), (
                                                            'asso_machine',
                                                            'asso_machine'),
                                                        ('nothing', 'nothing')],
                                   max_length=32, null=True, unique=True,
                                   verbose_name='Default profile'),
        ),
        migrations.AddField(
            model_name='modelswitch',
            name='commercial_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.CreateModel(
            name='ModuleOnSwitch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('slot',
                 models.CharField(help_text='Slot on switch', max_length=15,
                                  verbose_name='Slot')),
            ],
            options={
                'verbose_name': 'link between switchs and modules',
                'permissions': (
                    ('view_moduleonswitch',
                     'Can view a moduleonswitch object'),),
            },
            bases=(re2o.mixins.AclMixin, re2o.mixins.RevMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ModuleSwitch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('reference',
                 models.CharField(help_text='Reference of a module',
                                  max_length=255,
                                  verbose_name='Module reference')),
                ('comment', models.CharField(blank=True, help_text='Comment',
                                             max_length=255, null=True,
                                             verbose_name='Comment')),
            ],
            options={
                'verbose_name': 'switch module',
                'permissions': (
                    ('view_moduleswitch', 'Can view a switch module object'),),
                'verbose_name_plural': 'switch modules',
            },
            bases=(re2o.mixins.AclMixin, re2o.mixins.RevMixin, models.Model),
        ),
        migrations.AddField(
            model_name='modelswitch',
            name='is_itself_module',
            field=models.BooleanField(default=False,
                                      help_text='The switch is considered as a module.'),
        ),
        migrations.AddField(
            model_name='modelswitch',
            name='is_modular',
            field=models.BooleanField(default=False,
                                      help_text='The switch model is modular.'),
        ),
        migrations.AddField(
            model_name='moduleonswitch',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to='topologie.ModuleSwitch'),
        ),
        migrations.AddField(
            model_name='moduleonswitch',
            name='switch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    to='topologie.Switch'),
        ),
        migrations.AlterUniqueTogether(
            name='moduleonswitch',
            unique_together=set([('slot', 'switch')]),
        ),
        migrations.AlterModelOptions(
            name='moduleonswitch',
            options={'permissions': (('view_moduleonswitch',
                                      'Can view a link between switch and module object'),),
                     'verbose_name': 'link between switch and module',
                     'verbose_name_plural': 'links between switch and module'},
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='profil_default',
            field=models.CharField(blank=True, choices=[('room', 'Room'), (
                'access_point', 'Access point'), ('uplink', 'Uplink'), (
                                                            'asso_machine',
                                                            'Organisation machine'),
                                                        ('nothing', 'Nothing')],
                                   max_length=32, null=True, unique=True,
                                   verbose_name='Default profile'),
        ),
        migrations.AlterField(
            model_name='portprofile',
            name='radius_type',
            field=models.CharField(choices=[('NO', 'NO'), ('802.1X', '802.1X'),
                                            ('MAC-radius', 'MAC-RADIUS')],
                                   help_text='Type of RADIUS authentication : inactive, MAC-address or 802.1X',
                                   max_length=32, verbose_name='RADIUS type'),
        ),
        migrations.CreateModel(
            name='Dormitory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'dormitory',
                'permissions': (
                    ('view_dormitory', 'Can view a dormitory object'),),
                'verbose_name_plural': 'dormitories',
            },
            bases=(re2o.mixins.AclMixin, re2o.mixins.RevMixin, models.Model),
        ),
        migrations.AddField(
            model_name='building',
            name='dormitory',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='topologie.Dormitory'),
            preserve_default=False,
        ),
        migrations.RunPython(
            code=create_dormitory,
            reverse_code=delete_dormitory,
        ),
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AddField(
            model_name='room',
            name='building',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.PROTECT,
                                    to='topologie.Building'),
        ),
        migrations.AlterUniqueTogether(
            name='room',
            unique_together=set([('name', 'building')]),
        ),
        migrations.AlterField(
            model_name='building',
            name='dormitory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    to='topologie.Dormitory'),
        ),
        migrations.RunPython(
            code=transfer_room,
            reverse_code=untransfer_room,
        ),
        migrations.AlterField(
            model_name='room',
            name='building',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                    to='topologie.Building'),
        ),
    ]
