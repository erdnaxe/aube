# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2017  Maël Kervella

"""
Formulaires d'ajout, edition et suppressions de :
    - machines
    - interfaces
    - domain (noms de machine)
    - alias (cname)
    - service (dhcp, dns..)
    - ns (serveur dns)
    - mx (serveur mail)
    - ports ouverts et profils d'ouverture par interface
"""

from django import forms
from django.forms import ModelForm, Form
from django.utils.translation import ugettext_lazy as _

from re2o.field_permissions import FieldPermissionFormMixin
from re2o.mixins import FormRevMixin
from .models import (
    Domain,
    Machine,
    Interface,
    IpList,
    MachineType,
    Extension,
    Service,
    SshFp,
    IpType,
    Ipv6List,
)


class EditMachineForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Formulaire d'édition d'une machine"""

    class Meta:
        model = Machine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditMachineForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = _("Machine name")


class NewMachineForm(EditMachineForm):
    """Creation d'une machine, ne renseigne que le nom"""

    class Meta(EditMachineForm.Meta):
        fields = ['name']


class EditInterfaceForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Edition d'une interface. Edition complète"""

    class Meta:
        model = Interface
        fields = ['machine', 'machine_type', 'ipv4', 'mac_address', 'details']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        user = kwargs.get('user')
        super(EditInterfaceForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['mac_address'].label = _("MAC address")
        self.fields['machine_type'].label = _("Machine type")
        self.fields['machine_type'].empty_label = _("Select a machine type")
        if "ipv4" in self.fields:
            self.fields['ipv4'].empty_label = _("Automatic IPv4 assignment")
            self.fields['ipv4'].queryset = IpList.objects.filter(
                interface__isnull=True
            )
            can_use_all_iptype, _reason = IpType.can_use_all(user)
            if not can_use_all_iptype:
                self.fields['ipv4'].queryset = IpList.objects.filter(
                    interface__isnull=True
                ).filter(ip_type__in=IpType.objects.filter(need_infra=False))
            else:
                self.fields['ipv4'].queryset = IpList.objects.filter(
                    interface__isnull=True
                )
            # Add it's own address
            self.fields['ipv4'].queryset |= IpList.objects.filter(
                interface=self.instance
            )
        if "machine" in self.fields:
            self.fields['machine'].queryset = Machine.objects.all() \
                .select_related('user')
        can_use_all_machinetype, _reason = MachineType.can_use_all(user)
        if not can_use_all_machinetype:
            self.fields['machine_type'].queryset = MachineType.objects.filter(
                ip_type__in=IpType.objects.filter(need_infra=False)
            )


class AddInterfaceForm(EditInterfaceForm):
    """Ajout d'une interface à une machine. En fonction des droits,
    affiche ou non l'ensemble des ip disponibles"""

    class Meta(EditInterfaceForm.Meta):
        fields = ['machine_type', 'ipv4', 'mac_address', 'details']


class AliasForm(FormRevMixin, ModelForm):
    """Ajout d'un alias (et edition), CNAME, contenant nom et extension"""

    class Meta:
        model = Domain
        fields = ['name', 'extension']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        user = kwargs.pop('user')
        super(AliasForm, self).__init__(*args, prefix=prefix, **kwargs)
        can_use_all, _reason = Extension.can_use_all(user)
        if not can_use_all:
            self.fields['extension'].queryset = Extension.objects.filter(
                need_infra=False
            )


class DomainForm(FormRevMixin, ModelForm):
    """Ajout et edition d'un enregistrement de nom, relié à interface"""

    class Meta:
        model = Domain
        fields = ['name']

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs.pop('user')
            initial = kwargs.get('initial', {})
            initial['name'] = user.get_next_domain_name()
            kwargs['initial'] = initial
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(DomainForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelAliasForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs objets alias"""
    alias = forms.ModelMultipleChoiceField(
        queryset=Domain.objects.all(),
        label=_("Current aliases"),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        interface = kwargs.pop('interface')
        super(DelAliasForm, self).__init__(*args, **kwargs)
        self.fields['alias'].queryset = Domain.objects.filter(
            cname__in=Domain.objects.filter(interface_parent=interface)
        )


class Ipv6ListForm(FormRevMixin, FieldPermissionFormMixin, ModelForm):
    """Gestion des ipv6 d'une machine"""

    class Meta:
        model = Ipv6List
        fields = ['ipv6', 'slaac_ip']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(Ipv6ListForm, self).__init__(*args, prefix=prefix, **kwargs)


class ServiceForm(FormRevMixin, ModelForm):
    """Ajout et edition d'une classe de service : dns, dhcp, etc"""

    class Meta:
        model = Service
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ServiceForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['servers'].queryset = (Interface.objects.all()
            .select_related(
            'domain__extension'
        ))

    def save(self, commit=True):
        # TODO : None of the parents of ServiceForm use the commit
        # parameter in .save()
        instance = super(ServiceForm, self).save(commit=False)
        if commit:
            instance.save()
        instance.process_link(self.cleaned_data.get('servers'))
        return instance


class DelServiceForm(FormRevMixin, Form):
    """Suppression d'un ou plusieurs service"""
    service = forms.ModelMultipleChoiceField(
        queryset=Service.objects.none(),
        label=_("Current services"),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelServiceForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['service'].queryset = instances
        else:
            self.fields['service'].queryset = Service.objects.all()


class EditOuverturePortConfigForm(FormRevMixin, ModelForm):
    """Edition de la liste des profils d'ouverture de ports
    pour l'interface"""

    class Meta:
        model = Interface
        fields = ['port_lists']

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditOuverturePortConfigForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )


class SshFpForm(FormRevMixin, ModelForm):
    """Edits a SSHFP record."""

    class Meta:
        model = SshFp
        exclude = ('machine',)

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(SshFpForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
