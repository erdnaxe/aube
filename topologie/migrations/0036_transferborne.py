# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-12-31 19:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('topologie', '0035_auto_20180324_0023'),
    ]

    def transfer_bornes(apps, schema_editor):
        db_alias = schema_editor.connection.alias
        machinetype = apps.get_model("machines", "MachineType")
        borne = apps.get_model("topologie", "Borne")
        interface =  apps.get_model("machines", "Interface")
        bornes_list = machinetype.objects.using(db_alias).filter(type__icontains='borne')
        if bornes_list:
            for inter in interface.objects.using(db_alias).filter(type=bornes_list.first()):
                borne_object = borne()
                borne_object.interface_ptr_id = inter.pk
                borne_object.__dict__.update(inter.__dict__) 
                borne_object.save()

    def untransfer_bornes(apps, schema_editor):
        return

    operations = [
    migrations.RunPython(transfer_bornes, untransfer_bornes),
    ]