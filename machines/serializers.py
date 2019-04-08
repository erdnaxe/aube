# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""machines.serializers
Serializers for the Machines app
"""

from rest_framework import serializers

from machines.models import (
    Interface,
    IpType,
    Extension,
    IpList,
    Domain,
    Txt,
    Mx,
    Srv,
    Service_link,
    Ns,
    OuverturePort,
    Ipv6List
)


class IpTypeField(serializers.RelatedField):
    """ Serializer for an IpType object field """

    def to_representation(self, value):
        return value.type

    def to_internal_value(self, data):
        pass


class IpListSerializer(serializers.ModelSerializer):
    """ Serializer for an Ipv4List obejct using the IpType serialization """

    ip_type = IpTypeField(read_only=True)

    class Meta:
        model = IpList
        fields = ('ipv4', 'ip_type')


class Ipv6ListSerializer(serializers.ModelSerializer):
    """ Serializer for an Ipv6List object """

    class Meta:
        model = Ipv6List
        fields = ('ipv6', 'slaac_ip')


class InterfaceSerializer(serializers.ModelSerializer):
    """ Serializer for an Interface object. Use SerializerMethodField
    to get ForeignKey values """

    ipv4 = IpListSerializer(read_only=True)
    # TODO : use serializer.RelatedField to avoid duplicate code
    mac_address = serializers.SerializerMethodField('get_macaddress')
    domain = serializers.SerializerMethodField('get_dns')
    extension = serializers.SerializerMethodField('get_interface_extension')

    class Meta:
        model = Interface
        fields = ('ipv4', 'mac_address', 'domain', 'extension')

    @staticmethod
    def get_dns(obj):
        """ The name of the associated  DNS object """
        return obj.domain.name

    @staticmethod
    def get_interface_extension(obj):
        """ The name of the associated Interface object """
        return obj.domain.extension.name

    @staticmethod
    def get_macaddress(obj):
        """ The string representation of the associated MAC address """
        return str(obj.mac_address)


class FullInterfaceSerializer(serializers.ModelSerializer):
    """ Serializer for an Interface obejct. Use SerializerMethodField
    to get ForeignKey values """

    ipv4 = IpListSerializer(read_only=True)
    ipv6 = Ipv6ListSerializer(read_only=True, many=True)
    # TODO : use serializer.RelatedField to avoid duplicate code
    mac_address = serializers.SerializerMethodField('get_macaddress')
    domain = serializers.SerializerMethodField('get_dns')
    extension = serializers.SerializerMethodField('get_interface_extension')

    class Meta:
        model = Interface
        fields = ('ipv4', 'ipv6', 'mac_address', 'domain', 'extension')

    @staticmethod
    def get_dns(obj):
        """ The name of the associated DNS object """
        return obj.domain.name

    @staticmethod
    def get_interface_extension(obj):
        """ The name of the associated Extension object """
        return obj.domain.extension.name

    @staticmethod
    def get_macaddress(obj):
        """ The string representation of the associated MAC address """
        return str(obj.mac_address)


class ExtensionNameField(serializers.RelatedField):
    """ Serializer for Extension object field """

    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        pass


class TypeSerializer(serializers.ModelSerializer):
    """ Serializer for an IpType object. Use SerializerMethodField to
    get ForeignKey values. Infos about the general port policy is added """

    extension = ExtensionNameField(read_only=True)
    ouverture_ports_tcp_in = serializers \
        .SerializerMethodField('get_port_policy_input_tcp')
    ouverture_ports_tcp_out = serializers \
        .SerializerMethodField('get_port_policy_output_tcp')
    ouverture_ports_udp_in = serializers \
        .SerializerMethodField('get_port_policy_input_udp')
    ouverture_ports_udp_out = serializers \
        .SerializerMethodField('get_port_policy_output_udp')

    class Meta:
        model = IpType
        fields = ('type', 'extension', 'domaine_ip_start', 'domaine_ip_stop',
                  'prefix_v6',
                  'ouverture_ports_tcp_in', 'ouverture_ports_tcp_out',
                  'ouverture_ports_udp_in', 'ouverture_ports_udp_out',)

    @staticmethod
    def get_port_policy(obj, protocole, io):
        """ Generic utility function to get the policy for a given
        port, protocole and IN or OUT """
        if obj.ouverture_ports is None:
            return []
        return map(
            str,
            obj.ouverture_ports.ouvertureport_set.filter(
                protocole=protocole
            ).filter(io=io)
        )

    def get_port_policy_input_tcp(self, obj):
        """Renvoie la liste des ports ouverts en entrée tcp"""
        return self.get_port_policy(obj, OuverturePort.TCP, OuverturePort.IN)

    def get_port_policy_output_tcp(self, obj):
        """Renvoie la liste des ports ouverts en sortie tcp"""
        return self.get_port_policy(obj, OuverturePort.TCP, OuverturePort.OUT)

    def get_port_policy_input_udp(self, obj):
        """Renvoie la liste des ports ouverts en entrée udp"""
        return self.get_port_policy(obj, OuverturePort.UDP, OuverturePort.IN)

    def get_port_policy_output_udp(self, obj):
        """Renvoie la liste des ports ouverts en sortie udp"""
        return self.get_port_policy(obj, OuverturePort.UDP, OuverturePort.OUT)


class ExtensionSerializer(serializers.ModelSerializer):
    """Serialisation d'une extension : origin_ip et la zone sont
    des foreign_key donc evalués en get_..."""
    origin = serializers.SerializerMethodField('get_origin_ip')
    zone_entry = serializers.SerializerMethodField('get_zone_name')
    soa = serializers.SerializerMethodField('get_soa_data')

    class Meta:
        model = Extension
        fields = ('name', 'origin', 'origin_v6', 'zone_entry', 'soa')

    @staticmethod
    def get_origin_ip(obj):
        """ The IP of the associated origin for the zone """
        return obj.origin.ipv4

    @staticmethod
    def get_zone_name(obj):
        """ The name of the associated zone """
        return str(obj.dns_entry)

    @staticmethod
    def get_soa_data(obj):
        """ The representation of the associated SOA """
        return {'mail': obj.soa.dns_soa_mail, 'param': obj.soa.dns_soa_param}


class MxSerializer(serializers.ModelSerializer):
    """Serialisation d'un MX, evaluation du nom, de la zone
    et du serveur cible, etant des foreign_key"""
    name = serializers.SerializerMethodField('get_entry_name')
    zone = serializers.SerializerMethodField('get_zone_name')
    mx_entry = serializers.SerializerMethodField('get_mx_name')

    class Meta:
        model = Mx
        fields = ('zone', 'priority', 'name', 'mx_entry')

    @staticmethod
    def get_entry_name(obj):
        """ The name of the DNS MX entry """
        return str(obj.name)

    @staticmethod
    def get_zone_name(obj):
        """ The name of the associated zone of the MX record """
        return obj.zone.name

    @staticmethod
    def get_mx_name(obj):
        """ The string representation of the entry to add to the DNS """
        return str(obj.dns_entry)


class TxtSerializer(serializers.ModelSerializer):
    """Serialisation d'un txt : zone cible et l'entrée txt
    sont evaluées à part"""
    zone = serializers.SerializerMethodField('get_zone_name')
    txt_entry = serializers.SerializerMethodField('get_txt_name')

    class Meta:
        model = Txt
        fields = ('zone', 'txt_entry', 'field1', 'field2')

    @staticmethod
    def get_zone_name(obj):
        """ The name of the associated zone """
        return str(obj.zone.name)

    @staticmethod
    def get_txt_name(obj):
        """ The string representation of the entry to add to the DNS """
        return str(obj.dns_entry)


class SrvSerializer(serializers.ModelSerializer):
    """Serialisation d'un srv : zone cible et l'entrée txt"""
    extension = serializers.SerializerMethodField('get_extension_name')
    srv_entry = serializers.SerializerMethodField('get_srv_name')

    class Meta:
        model = Srv
        fields = (
            'service',
            'protocole',
            'extension',
            'ttl',
            'priority',
            'weight',
            'port',
            'target',
            'srv_entry'
        )

    @staticmethod
    def get_extension_name(obj):
        """ The name of the associated extension """
        return str(obj.extension.name)

    @staticmethod
    def get_srv_name(obj):
        """ The string representation of the entry to add to the DNS """
        return str(obj.dns_entry)


class NsSerializer(serializers.ModelSerializer):
    """Serialisation d'un NS : la zone, l'entrée ns complète et le serveur
    ns sont évalués à part"""
    zone = serializers.SerializerMethodField('get_zone_name')
    ns = serializers.SerializerMethodField('get_domain_name')
    ns_entry = serializers.SerializerMethodField('get_text_name')

    class Meta:
        model = Ns
        fields = ('zone', 'ns', 'ns_entry')

    @staticmethod
    def get_zone_name(obj):
        """ The name of the associated zone """
        return obj.zone.name

    @staticmethod
    def get_domain_name(obj):
        """ The name of the associated NS target """
        return str(obj.ns)

    @staticmethod
    def get_text_name(obj):
        """ The string representation of the entry to add to the DNS """
        return str(obj.dns_entry)


class DomainSerializer(serializers.ModelSerializer):
    """Serialisation d'un domain, extension, cname sont des foreign_key,
    et l'entrée complète, sont évalués à part"""
    extension = serializers.SerializerMethodField('get_zone_name')
    cname = serializers.SerializerMethodField('get_alias_name')
    cname_entry = serializers.SerializerMethodField('get_cname_name')

    class Meta:
        model = Domain
        fields = ('name', 'extension', 'cname', 'cname_entry')

    @staticmethod
    def get_zone_name(obj):
        """ The name of the associated zone """
        return obj.extension.name

    @staticmethod
    def get_alias_name(obj):
        """ The name of the associated alias """
        return str(obj.cname)

    @staticmethod
    def get_cname_name(obj):
        """ The name of the associated CNAME target """
        return str(obj.dns_entry)


class ServiceServersSerializer(serializers.ModelSerializer):
    """Evaluation d'un Service, et serialisation"""
    server = serializers.SerializerMethodField('get_server_name')
    service = serializers.SerializerMethodField('get_service_name')
    need_regen = serializers.SerializerMethodField('get_regen_status')

    class Meta:
        model = Service_link
        fields = ('server', 'service', 'need_regen')

    @staticmethod
    def get_server_name(obj):
        """ The name of the associated server """
        return str(obj.server.domain.name)

    @staticmethod
    def get_service_name(obj):
        """ The name of the service name """
        return str(obj.service)

    @staticmethod
    def get_regen_status(obj):
        """ The string representation of the regen status """
        return obj.need_regen


class OuverturePortsSerializer(serializers.Serializer):
    """Serialisation de l'ouverture des ports"""
    ipv4 = serializers.SerializerMethodField()
    ipv6 = serializers.SerializerMethodField()

    def create(self, validated_data):
        """ Creates a new object based on the un-serialized data.
        Used to implement an abstract inherited method """
        pass

    def update(self, instance, validated_data):
        """ Updates an object based on the un-serialized data.
        Used to implement an abstract inherited method """
        pass

    @staticmethod
    def get_ipv4():
        """ The representation of the policy for the IPv4 addresses """
        return {
            i.ipv4.ipv4: {
                "tcp_in": [j.tcp_ports_in() for j in i.port_lists.all()],
                "tcp_out": [j.tcp_ports_out() for j in i.port_lists.all()],
                "udp_in": [j.udp_ports_in() for j in i.port_lists.all()],
                "udp_out": [j.udp_ports_out() for j in i.port_lists.all()],
            }
            for i in Interface.objects.all() if i.ipv4
        }

    @staticmethod
    def get_ipv6():
        """ The representation of the policy for the IPv6 addresses """
        return {
            i.ipv6: {
                "tcp_in": [j.tcp_ports_in() for j in i.port_lists.all()],
                "tcp_out": [j.tcp_ports_out() for j in i.port_lists.all()],
                "udp_in": [j.udp_ports_in() for j in i.port_lists.all()],
                "udp_out": [j.udp_ports_out() for j in i.port_lists.all()],
            }
            for i in Interface.objects.all() if i.ipv6
        }
