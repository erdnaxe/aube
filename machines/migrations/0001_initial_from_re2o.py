# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-04-08 16:05
from __future__ import unicode_literals

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import macaddress.fields
import re2o.field_permissions
import re2o.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'DNAME record',
                'verbose_name_plural': 'DNAME records',
                'permissions': (('view_dname', 'Can view a DNAME record object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Mandatory and unique, must not contain dots.', max_length=255)),
            ],
            options={
                'verbose_name': 'domain',
                'verbose_name_plural': 'domains',
                'permissions': (('view_domain', 'Can view a domain object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Extension',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Zone name, must begin with a dot (.example.org)', max_length=255, unique=True)),
                ('need_infra', models.BooleanField(default=False)),
                ('origin_v6', models.GenericIPAddressField(blank=True, help_text='AAAA record associated with the zone', null=True, protocol='IPv6')),
                ('dnssec', models.BooleanField(default=False, help_text='Should the zone be signed with DNSSEC')),
            ],
            options={
                'verbose_name': 'DNS extension',
                'verbose_name_plural': 'DNS extensions',
                'permissions': (('view_extension', 'Can view an extension object'), ('use_all_extension', 'Can use all extensions')),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Interface',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac_address', macaddress.fields.MACAddressField(integer=False, max_length=17)),
                ('details', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'verbose_name': 'interface',
                'verbose_name_plural': 'interfaces',
                'permissions': (('view_interface', 'Can view an interface object'), ('change_interface_machine', 'Can change the owner of an interface')),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, re2o.field_permissions.FieldPermissionModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='IpList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ipv4', models.GenericIPAddressField(protocol='IPv4', unique=True)),
            ],
            options={
                'verbose_name': 'IPv4 addresses list',
                'verbose_name_plural': 'IPv4 addresses lists',
                'permissions': (('view_iplist', 'Can view an IPv4 addresses list object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='IpType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('need_infra', models.BooleanField(default=False)),
                ('domaine_ip_start', models.GenericIPAddressField(protocol='IPv4')),
                ('domaine_ip_stop', models.GenericIPAddressField(protocol='IPv4')),
                ('domaine_ip_network', models.GenericIPAddressField(blank=True, help_text="Network containing the domain's IPv4 range (optional)", null=True, protocol='IPv4')),
                ('domaine_ip_netmask', models.IntegerField(default=24, help_text="Netmask for the domain's IPv4 range", validators=[django.core.validators.MaxValueValidator(31), django.core.validators.MinValueValidator(8)])),
                ('reverse_v4', models.BooleanField(default=False, help_text='Enable reverse DNS for IPv4')),
                ('prefix_v6', models.GenericIPAddressField(blank=True, null=True, protocol='IPv6')),
                ('prefix_v6_length', models.IntegerField(default=64, validators=[django.core.validators.MaxValueValidator(128), django.core.validators.MinValueValidator(0)])),
                ('reverse_v6', models.BooleanField(default=False, help_text='Enable reverse DNS for IPv6')),
            ],
            options={
                'verbose_name': 'IP type',
                'verbose_name_plural': 'IP types',
                'permissions': (('view_iptype', 'Can view an IP type object'), ('use_all_iptype', 'Can use all IP types')),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Ipv6List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ipv6', models.GenericIPAddressField(protocol='IPv6')),
                ('slaac_ip', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'IPv6 addresses list',
                'verbose_name_plural': 'IPv6 addresses lists',
                'permissions': (('view_ipv6list', 'Can view an IPv6 addresses list object'), ('change_ipv6list_slaac_ip', 'Can change the SLAAC value of an IPv6 addresses list')),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, re2o.field_permissions.FieldPermissionModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='Optional', max_length=255, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'machine',
                'verbose_name_plural': 'machines',
                'permissions': (('view_machine', 'Can view a machine object'), ('change_machine_user', 'Can change the user of a machine')),
            },
            bases=(re2o.mixins.RevMixin, re2o.field_permissions.FieldPermissionModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='MachineType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('ip_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='machines.IpType')),
            ],
            options={
                'verbose_name': 'machine type',
                'verbose_name_plural': 'machine types',
                'permissions': (('view_machinetype', 'Can view a machine type object'), ('use_all_machinetype', 'Can use all machine types')),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Mx',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField()),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='machines.Domain')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='machines.Extension')),
            ],
            options={
                'verbose_name': 'MX record',
                'verbose_name_plural': 'MX records',
                'permissions': (('view_mx', 'Can view an MX record object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Nas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('port_access_mode', models.CharField(choices=[('802.1X', '802.1X'), ('Mac-address', 'MAC-address')], default='802.1X', max_length=32)),
                ('autocapture_mac', models.BooleanField(default=False)),
                ('machine_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='machinetype_on_nas', to='machines.MachineType')),
                ('nas_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='nas_type', to='machines.MachineType')),
            ],
            options={
                'verbose_name': 'NAS device',
                'verbose_name_plural': 'NAS devices',
                'permissions': (('view_nas', 'Can view a NAS device object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Ns',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ns', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='machines.Domain')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='machines.Extension')),
            ],
            options={
                'verbose_name': 'NS record',
                'verbose_name_plural': 'NS records',
                'permissions': (('view_ns', 'Can view an NS record object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OuverturePort',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(65535)])),
                ('end', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(65535)])),
                ('protocole', models.CharField(choices=[('T', 'TCP'), ('U', 'UDP')], default='T', max_length=1)),
                ('io', models.CharField(choices=[('I', 'IN'), ('O', 'OUT')], default='O', max_length=1)),
            ],
            options={
                'verbose_name': 'ports opening',
                'verbose_name_plural': 'ports openings',
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OuverturePortList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the ports configuration', max_length=255)),
            ],
            options={
                'verbose_name': 'ports opening list',
                'verbose_name_plural': 'ports opening lists',
                'permissions': (('view_ouvertureportlist', 'Can view a ports opening list object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_type', models.CharField(max_length=255, unique=True)),
                ('specific_role', models.CharField(blank=True, choices=[('dhcp-server', 'DHCP server'), ('switch-conf-server', 'Switches configuration server'), ('dns-recursive-server', 'Recursive DNS server'), ('ntp-server', 'NTP server'), ('radius-server', 'RADIUS server'), ('log-server', 'Log server'), ('ldap-master-server', 'LDAP master server'), ('ldap-backup-server', 'LDAP backup server'), ('smtp-server', 'SMTP server'), ('postgresql-server', 'postgreSQL server'), ('mysql-server', 'mySQL server'), ('sql-client', 'SQL client'), ('gateway', 'Gateway')], max_length=32, null=True)),
                ('servers', models.ManyToManyField(to='machines.Interface')),
            ],
            options={
                'verbose_name': 'server role',
                'verbose_name_plural': 'server roles',
                'permissions': (('view_role', 'Can view a role object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_type', models.CharField(blank=True, max_length=255, unique=True)),
                ('min_time_regen', models.DurationField(default=datetime.timedelta(0, 60), help_text='Minimal time before regeneration of the service.')),
                ('regular_time_regen', models.DurationField(default=datetime.timedelta(0, 3600), help_text='Maximal time before regeneration of the service.')),
            ],
            options={
                'verbose_name': 'service to generate (DHCP, DNS, ...)',
                'verbose_name_plural': 'services to generate (DHCP, DNS, ...)',
                'permissions': (('view_service', 'Can view a service object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Service_link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_regen', models.DateTimeField(auto_now_add=True)),
                ('asked_regen', models.BooleanField(default=False)),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machines.Interface')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machines.Service')),
            ],
            options={
                'verbose_name': 'link between service and server',
                'verbose_name_plural': 'links between service and server',
                'permissions': (('view_service_link', 'Can view a service server link object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SOA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('mail', models.EmailField(help_text='Contact email address for the zone', max_length=254)),
                ('refresh', models.PositiveIntegerField(default=86400, help_text='Seconds before the secondary DNS have to ask the primary DNS serial to detect a modification')),
                ('retry', models.PositiveIntegerField(default=7200, help_text='Seconds before the secondary DNS ask the serial again in case of a primary DNS timeout')),
                ('expire', models.PositiveIntegerField(default=3600000, help_text='Seconds before the secondary DNS stop answering requests in case of primary DNS timeout')),
                ('ttl', models.PositiveIntegerField(default=172800, help_text='Time to Live')),
            ],
            options={
                'verbose_name': 'SOA record',
                'verbose_name_plural': 'SOA records',
                'permissions': (('view_soa', 'Can view an SOA record object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Srv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(max_length=31)),
                ('protocole', models.CharField(choices=[('TCP', 'TCP'), ('UDP', 'UDP')], default='TCP', max_length=3)),
                ('ttl', models.PositiveIntegerField(default=172800, help_text='Time to Live')),
                ('priority', models.PositiveIntegerField(default=0, help_text='Priority of the target server (positive integer value, the lower it is, the more the server will be used if available)', validators=[django.core.validators.MaxValueValidator(65535)])),
                ('weight', models.PositiveIntegerField(default=0, help_text='Relative weight for records with the same priority (integer value between 0 and 65535)', validators=[django.core.validators.MaxValueValidator(65535)])),
                ('port', models.PositiveIntegerField(help_text='TCP/UDP port', validators=[django.core.validators.MaxValueValidator(65535)])),
                ('extension', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='machines.Extension')),
                ('target', models.ForeignKey(help_text='Target server', on_delete=django.db.models.deletion.PROTECT, to='machines.Domain')),
            ],
            options={
                'verbose_name': 'SRV record',
                'verbose_name_plural': 'SRV records',
                'permissions': (('view_srv', 'Can view an SRV record object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SshFp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_key_entry', models.TextField(help_text='SSH public key', max_length=2048)),
                ('algo', models.CharField(choices=[('ssh-rsa', 'ssh-rsa'), ('ssh-ed25519', 'ssh-ed25519'), ('ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp256'), ('ecdsa-sha2-nistp384', 'ecdsa-sha2-nistp384'), ('ecdsa-sha2-nistp521', 'ecdsa-sha2-nistp521')], max_length=32)),
                ('comment', models.CharField(blank=True, help_text='Comment', max_length=255, null=True)),
                ('machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machines.Machine')),
            ],
            options={
                'verbose_name': 'SSHFP record',
                'verbose_name_plural': 'SSHFP records',
                'permissions': (('view_sshfp', 'Can view an SSHFP record object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Txt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field1', models.CharField(max_length=255)),
                ('field2', models.TextField(max_length=2047)),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='machines.Extension')),
            ],
            options={
                'verbose_name': 'TXT record',
                'verbose_name_plural': 'TXT records',
                'permissions': (('view_txt', 'Can view a TXT record object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Vlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vlan_id', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(4095)])),
                ('name', models.CharField(max_length=256)),
                ('comment', models.CharField(blank=True, max_length=256)),
                ('arp_protect', models.BooleanField(default=False)),
                ('dhcp_snooping', models.BooleanField(default=False)),
                ('dhcpv6_snooping', models.BooleanField(default=False)),
                ('igmp', models.BooleanField(default=False, help_text='v4 multicast management')),
                ('mld', models.BooleanField(default=False, help_text='v6 multicast management')),
            ],
            options={
                'verbose_name': 'VLAN',
                'verbose_name_plural': 'VLANs',
                'permissions': (('view_vlan', 'Can view a VLAN object'),),
            },
            bases=(re2o.mixins.RevMixin, re2o.mixins.AclMixin, models.Model),
        ),
        migrations.AddField(
            model_name='service',
            name='servers',
            field=models.ManyToManyField(through='machines.Service_link', to='machines.Interface'),
        ),
        migrations.AddField(
            model_name='ouvertureport',
            name='port_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machines.OuverturePortList'),
        ),
    ]
