# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2016-2018  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2017-2018  Maël Kervella
# Copyright © 2018  Charlie Jacomme

"""machines.views
The views for the Machines app
"""

from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import ProtectedError, F
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer

from preferences.models import GeneralOption
from re2o.acl import (
    can_create,
    can_edit,
    can_view,
    can_delete,
    can_view_all,
    can_delete_set,
)
from re2o.utils import (
    all_active_assigned_interfaces,
    filter_active_interfaces,
)
from re2o.base import (
    SortTable,
    re2o_paginator,
)
from re2o.views import form
from users.models import User
from .forms import (
    NewMachineForm,
    EditMachineForm,
    EditInterfaceForm,
    AddInterfaceForm,
    ExtensionForm,
    DelExtensionForm,
    EditIpTypeForm,
    IpTypeForm,
    DelIpTypeForm,
    DomainForm,
    AliasForm,
    DelAliasForm,
    NsForm,
    DelNsForm,
    TxtForm,
    DelTxtForm,
    DNameForm,
    DelDNameForm,
    MxForm,
    DelMxForm,
    RoleForm,
    DelRoleForm,
    ServiceForm,
    DelServiceForm,
    SshFpForm,
    SrvForm,
    DelSrvForm,
    Ipv6ListForm,
    EditOuverturePortListForm,
    EditOuverturePortConfigForm,
)
from .models import (
    IpType,
    Machine,
    Interface,
    Extension,
    SOA,
    Mx,
    Ns,
    Domain,
    Role,
    Service,
    Service_link,
    regen,
    Txt,
    DName,
    Srv,
    SshFp,
    OuverturePortList,
    OuverturePort,
    Ipv6List,
)
from .serializers import (
    FullInterfaceSerializer,
    InterfaceSerializer,
    TypeSerializer,
    DomainSerializer,
    TxtSerializer,
    SrvSerializer,
    MxSerializer,
    ExtensionSerializer,
    ServiceServersSerializer,
    NsSerializer,
)


def f_type_id(is_type_tt):
    """ The id that will be used in HTML to store the value of the field
    type. Depends on the fact that type is generate using typeahead or not
    """
    return 'id_Interface-machine_type_hidden' if is_type_tt else 'id_Interface-machine_type'


def generate_ipv4_choices(form_obj):
    """ Generate the parameter choices for the massive_bootstrap_form tag
    """
    f_ipv4 = form_obj.fields['ipv4']
    used_mtype_id = []
    choices = '{"":[{key:"",value:"' + _("Select a machine type first.") + '"}'
    mtype_id = -1

    for ip in (f_ipv4.queryset
            .annotate(mtype_id=F('ip_type__machinetype__id'))
            .order_by('mtype_id', 'id')):
        if mtype_id != ip.mtype_id:
            mtype_id = ip.mtype_id
            used_mtype_id.append(mtype_id)
            choices += '],"{t}":[{{key:"",value:"{v}"}},'.format(
                t=mtype_id,
                v=f_ipv4.empty_label or '""'
            )
        choices += '{{key:{k},value:"{v}"}},'.format(
            k=ip.id,
            v=ip.ipv4
        )

    for t in form_obj.fields['machine_type'].queryset.exclude(id__in=used_mtype_id):
        choices += '], "' + str(t.id) + '": ['
        choices += '{key: "", value: "' + str(f_ipv4.empty_label) + '"},'
    choices += ']}'
    return choices


def generate_ipv4_engine(is_type_tt):
    """ Generate the parameter engine for the massive_bootstrap_form tag
    """
    return (
        'new Bloodhound( {{'
        'datumTokenizer: Bloodhound.tokenizers.obj.whitespace( "value" ),'
        'queryTokenizer: Bloodhound.tokenizers.whitespace,'
        'local: choices_ipv4[ $( "#{machine_type_id}" ).val() ],'
        'identify: function( obj ) {{ return obj.key; }}'
        '}} )'
    ).format(
        machine_type_id=f_type_id(is_type_tt)
    )


def generate_ipv4_match_func(is_type_tt):
    """ Generate the parameter match_func for the massive_bootstrap_form tag
    """
    return (
        'function(q, sync) {{'
        'if (q === "") {{'
        'var first = choices_ipv4[$("#{machine_type_id}").val()].slice(0, 5);'
        'first = first.map( function (obj) {{ return obj.key; }} );'
        'sync(engine_ipv4.get(first));'
        '}} else {{'
        'engine_ipv4.search(q, sync);'
        '}}'
        '}}'
    ).format(
        machine_type_id=f_type_id(is_type_tt)
    )


def generate_ipv4_mbf_param(form_obj, is_type_tt):
    """ Generate all the parameters to use with the massive_bootstrap_form
    tag """
    i_choices = {'ipv4': generate_ipv4_choices(form_obj)}
    i_engine = {'ipv4': generate_ipv4_engine(is_type_tt)}
    i_match_func = {'ipv4': generate_ipv4_match_func(is_type_tt)}
    i_update_on = {'ipv4': [f_type_id(is_type_tt)]}
    i_gen_select = {'ipv4': False}
    i_mbf_param = {
        'choices': i_choices,
        'engine': i_engine,
        'match_func': i_match_func,
        'update_on': i_update_on,
        'gen_select': i_gen_select
    }
    return i_mbf_param


@login_required
@can_create(Machine)
@can_edit(User)
def new_machine(request, user, **_kwargs):
    """ Fonction de creation d'une machine. Cree l'objet machine,
    le sous objet interface et l'objet domain à partir de model forms.
    Trop complexe, devrait être simplifié"""

    machine = NewMachineForm(request.POST or None, user=request.user)
    interface = AddInterfaceForm(
        request.POST or None,
        user=request.user
    )
    domain = DomainForm(request.POST or None, user=user)
    if machine.is_valid() and interface.is_valid():
        new_machine_obj = machine.save(commit=False)
        new_machine_obj.user = user
        new_interface_obj = interface.save(commit=False)
        domain.instance.interface_parent = new_interface_obj
        if domain.is_valid():
            new_domain = domain.save(commit=False)
            new_machine_obj.save()
            new_interface_obj.machine = new_machine_obj
            new_interface_obj.save()
            new_domain.interface_parent = new_interface_obj
            new_domain.save()
            messages.success(request, _("The machine was created."))
            return redirect(reverse(
                'users:profil',
                kwargs={'userid': str(user.id)}
            ))
    i_mbf_param = generate_ipv4_mbf_param(interface, False)
    return form(
        {
            'machineform': machine,
            'interfaceform': interface,
            'domainform': domain,
            'i_mbf_param': i_mbf_param,
            'action_name': _("Create a machine")
        },
        'machines/machine.html',
        request
    )


@login_required
@can_edit(Interface)
def edit_interface(request, interface_instance, **_kwargs):
    """ Edition d'une interface. Distingue suivant les droits les valeurs
    de interfaces et machines que l'user peut modifier infra permet de
    modifier le propriétaire"""

    machine_form = EditMachineForm(
        request.POST or None,
        instance=interface_instance.machine,
        user=request.user
    )
    interface_form = EditInterfaceForm(
        request.POST or None,
        instance=interface_instance,
        user=request.user
    )
    domain_form = DomainForm(
        request.POST or None,
        instance=interface_instance.domain
    )
    if (machine_form.is_valid() and
            interface_form.is_valid() and
            domain_form.is_valid()):
        new_machine_obj = machine_form.save(commit=False)
        new_interface_obj = interface_form.save(commit=False)
        new_domain_obj = domain_form.save(commit=False)
        if machine_form.changed_data:
            new_machine_obj.save()
        if interface_form.changed_data:
            new_interface_obj.save()
        if domain_form.changed_data:
            new_domain_obj.save()
        messages.success(request, _("The machine was edited."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(interface_instance.machine.user.id)}
        ))
    i_mbf_param = generate_ipv4_mbf_param(interface_form, False)
    return form(
        {
            'machineform': machine_form,
            'interfaceform': interface_form,
            'domainform': domain_form,
            'i_mbf_param': i_mbf_param,
            'action_name': _("Edit")
        },
        'machines/machine.html',
        request
    )


@login_required
@can_delete(Machine)
def del_machine(request, machine, **_kwargs):
    """ Supprime une machine, interfaces en mode cascade"""
    if request.method == "POST":
        machine.delete()
        messages.success(request, _("The machine was deleted."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(machine.user.id)}
        ))
    return form(
        {'objet': machine, 'objet_name': 'machine'},
        'machines/delete.html',
        request
    )


@login_required
@can_create(Interface)
@can_edit(Machine)
def new_interface(request, machine, **_kwargs):
    """ Ajoute une interface et son domain associé à une machine existante"""

    interface_form = AddInterfaceForm(request.POST or None, user=request.user)
    domain_form = DomainForm(request.POST or None)
    if interface_form.is_valid():
        new_interface_obj = interface_form.save(commit=False)
        domain_form.instance.interface_parent = new_interface_obj
        new_interface_obj.machine = machine
        if domain_form.is_valid():
            new_domain_obj = domain_form.save(commit=False)
            new_interface_obj.save()
            new_domain_obj.interface_parent = new_interface_obj
            new_domain_obj.save()
            messages.success(request, _("The interface was created."))
            return redirect(reverse(
                'users:profil',
                kwargs={'userid': str(machine.user.id)}
            ))
    i_mbf_param = generate_ipv4_mbf_param(interface_form, False)
    return form(
        {
            'interfaceform': interface_form,
            'domainform': domain_form,
            'i_mbf_param': i_mbf_param,
            'action_name': _("Create an interface")
        },
        'machines/machine.html',
        request
    )


@login_required
@can_delete(Interface)
def del_interface(request, interface, **_kwargs):
    """ Supprime une interface. Domain objet en mode cascade"""
    if request.method == "POST":
        machine = interface.machine
        interface.delete()
        if not machine.interface_set.all():
            machine.delete()
        messages.success(request, _("The interface was deleted."))
        return redirect(reverse(
            'users:profil',
            kwargs={'userid': str(request.user.id)}
        ))
    return form(
        {'objet': interface, 'objet_name': 'interface'},
        'machines/delete.html',
        request
    )


@login_required
@can_create(Ipv6List)
@can_edit(Interface)
def new_ipv6list(request, interface, **_kwargs):
    """Nouvelle ipv6"""
    ipv6list_instance = Ipv6List(interface=interface)
    ipv6 = Ipv6ListForm(
        request.POST or None,
        instance=ipv6list_instance,
        user=request.user
    )
    if ipv6.is_valid():
        ipv6.save()
        messages.success(request, _("The IPv6 addresses list was created."))
        return redirect(reverse(
            'machines:index-ipv6',
            kwargs={'interfaceid': str(interface.id)}
        ))
    return form(
        {'ipv6form': ipv6, 'action_name': _("Create an IPv6 addresses list")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(Ipv6List)
def edit_ipv6list(request, ipv6list_instance, **_kwargs):
    """Edition d'une ipv6"""
    ipv6 = Ipv6ListForm(
        request.POST or None,
        instance=ipv6list_instance,
        user=request.user
    )
    if ipv6.is_valid():
        if ipv6.changed_data:
            ipv6.save()
            messages.success(request, _("The IPv6 addresses list was edited."))
        return redirect(reverse(
            'machines:index-ipv6',
            kwargs={'interfaceid': str(ipv6list_instance.interface.id)}
        ))
    return form(
        {'ipv6form': ipv6, 'action_name': _("Edit")},
        'machines/machine.html',
        request
    )


@login_required
@can_delete(Ipv6List)
def del_ipv6list(request, ipv6list, **_kwargs):
    """ Supprime une ipv6"""
    if request.method == "POST":
        interfaceid = ipv6list.interface.id
        ipv6list.delete()
        messages.success(request, _("The IPv6 addresses list was deleted."))
        return redirect(reverse(
            'machines:index-ipv6',
            kwargs={'interfaceid': str(interfaceid)}
        ))
    return form(
        {'objet': ipv6list, 'objet_name': 'ipv6'},
        'machines/delete.html',
        request
    )


@login_required
@can_create(SshFp)
@can_edit(Machine)
def new_sshfp(request, machine, **_kwargs):
    """Creates an SSHFP record associated with a machine"""
    sshfp_instance = SshFp(machine=machine)
    sshfp = SshFpForm(
        request.POST or None,
        instance=sshfp_instance
    )
    if sshfp.is_valid():
        sshfp.save()
        messages.success(request, _("The SSHFP record was created."))
        return redirect(reverse(
            'machines:index-sshfp',
            kwargs={'machineid': str(machine.id)}
        ))
    return form(
        {'sshfpform': sshfp, 'action_name': _("Create a SSHFP record")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(SshFp)
def edit_sshfp(request, sshfp_instance, **_kwargs):
    """Edits an SSHFP record"""
    sshfp = SshFpForm(
        request.POST or None,
        instance=sshfp_instance
    )
    if sshfp.is_valid():
        if sshfp.changed_data:
            sshfp.save()
            messages.success(request, _("The SSHFP record was edited."))
        return redirect(reverse(
            'machines:index-sshfp',
            kwargs={'machineid': str(sshfp_instance.machine.id)}
        ))
    return form(
        {'sshfpform': sshfp, 'action_name': _("Edit")},
        'machines/machine.html',
        request
    )


@login_required
@can_delete(SshFp)
def del_sshfp(request, sshfp, **_kwargs):
    """Deletes an SSHFP record"""
    if request.method == "POST":
        machineid = sshfp.machine.id
        sshfp.delete()
        messages.success(request, _("The SSHFP record was deleted."))
        return redirect(reverse(
            'machines:index-sshfp',
            kwargs={'machineid': str(machineid)}
        ))
    return form(
        {'objet': sshfp, 'objet_name': 'sshfp'},
        'machines/delete.html',
        request
    )


@login_required
@can_create(IpType)
def add_iptype(request):
    """ Ajoute un range d'ip. Intelligence dans le models, fonction views
    minimaliste"""

    iptype = IpTypeForm(request.POST or None)
    if iptype.is_valid():
        iptype.save()
        messages.success(request, _("The IP type was created."))
        return redirect(reverse('machines:index-iptype'))
    return form(
        {'iptypeform': iptype, 'action_name': _("Create an IP type")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(IpType)
def edit_iptype(request, iptype_instance, **_kwargs):
    """ Edition d'un range. Ne permet pas de le redimensionner pour éviter
    l'incohérence"""

    iptype = EditIpTypeForm(request.POST or None, instance=iptype_instance)
    if iptype.is_valid():
        if iptype.changed_data:
            iptype.save()
            messages.success(request, _("The IP type was edited."))
        return redirect(reverse('machines:index-iptype'))
    return form(
        {'iptypeform': iptype, 'action_name': _("Edit")},
        'machines/machine.html',
        request
    )


@login_required
@can_delete_set(IpType)
def del_iptype(request, instances):
    """ Suppression d'un range ip. Supprime les objets ip associés"""
    iptype = DelIpTypeForm(request.POST or None, instances=instances)
    if iptype.is_valid():
        iptype_dels = iptype.cleaned_data['iptypes']
        for iptype_del in iptype_dels:
            try:
                iptype_del.delete()
                messages.success(request, _("The IP type was deleted."))
            except ProtectedError:
                messages.error(
                    request,
                    (_("The IP type %s is assigned to at least one machine,"
                       " you can't delete it.") % iptype_del)
                )
        return redirect(reverse('machines:index-iptype'))
    return form(
        {'iptypeform': iptype, 'action_name': _("Delete")},
        'machines/machine.html',
        request
    )


@login_required
@can_create(Extension)
def add_extension(request):
    """ View used to add an Extension object """
    extension = ExtensionForm(request.POST or None)
    if extension.is_valid():
        extension.save()
        messages.success(request, _("The extension was created."))
        return redirect(reverse('machines:index-extension'))
    return form(
        {'extensionform': extension, 'action_name': _("Create an extension")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(Extension)
def edit_extension(request, extension_instance, **_kwargs):
    """ View used to edit an Extension object """
    extension = ExtensionForm(
        request.POST or None,
        instance=extension_instance
    )
    if extension.is_valid():
        if extension.changed_data:
            extension.save()
            messages.success(request, _("The extension was edited."))
        return redirect(reverse('machines:index-extension'))
    return form(
        {'extensionform': extension, 'action_name': _("Edit")},
        'machines/machine.html',
        request
    )


@login_required
@can_delete_set(Extension)
def del_extension(request, instances):
    """ View used to delete an Extension object """
    extension = DelExtensionForm(request.POST or None, instances=instances)
    if extension.is_valid():
        extension_dels = extension.cleaned_data['extensions']
        for extension_del in extension_dels:
            try:
                extension_del.delete()
                messages.success(request, _("The extension was deleted."))
            except ProtectedError:
                messages.error(
                    request,
                    (_("The extension %s is assigned to at least one machine"
                       " type, you can't delete it." % extension_del))
                )
        return redirect(reverse('machines:index-extension'))
    return form(
        {'extensionform': extension, 'action_name': _("Delete")},
        'machines/machine.html',
        request
    )


@login_required
@can_create(Mx)
def add_mx(request):
    """ View used to add a MX object """
    mx = MxForm(request.POST or None)
    if mx.is_valid():
        mx.save()
        messages.success(request, _("The MX record was created."))
        return redirect(reverse('machines:index-extension'))
    return form(
        {'mxform': mx, 'action_name': _("Create an MX record")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(Mx)
def edit_mx(request, mx_instance, **_kwargs):
    """ View used to edit a MX object """
    mx = MxForm(request.POST or None, instance=mx_instance)
    if mx.is_valid():
        if mx.changed_data:
            mx.save()
            messages.success(request, _("The MX record was edited."))
        return redirect(reverse('machines:index-extension'))
    return form(
        {'mxform': mx, 'action_name': _("Edit")},
        'machines/machine.html',
        request
    )


@login_required
@can_delete_set(Mx)
def del_mx(request, instances):
    """ View used to delete a MX object """
    mx = DelMxForm(request.POST or None, instances=instances)
    if mx.is_valid():
        mx_dels = mx.cleaned_data['mx']
        for mx_del in mx_dels:
            try:
                mx_del.delete()
                messages.success(request, _("The MX record was deleted."))
            except ProtectedError:
                messages.error(
                    request,
                    (_("Error: the MX record %s can't be deleted.") % mx_del)
                )
        return redirect(reverse('machines:index-extension'))
    return form(
        {'mxform': mx, 'action_name': _("Delete")},
        'machines/machine.html',
        request
    )


@login_required
@can_create(Ns)
def add_ns(request):
    """ View used to add a NS object """
    ns = NsForm(request.POST or None)
    if ns.is_valid():
        ns.save()
        messages.success(request, _("The NS record was created."))
        return redirect(reverse('machines:index-extension'))
    return form(
        {'nsform': ns, 'action_name': _("Create an NS record")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(Ns)
def edit_ns(request, ns_instance, **_kwargs):
    """ View used to edit a NS object """
    ns = NsForm(request.POST or None, instance=ns_instance)
    if ns.is_valid():
        if ns.changed_data:
            ns.save()
            messages.success(request, _("The NS record was edited."))
        return redirect(reverse('machines:index-extension'))
    return form(
        {'nsform': ns, 'action_name': _("Edit")},
        'machines/machine.html',
        request
    )


@login_required
@can_delete_set(Ns)
def del_ns(request, instances):
    """ View used to delete a NS object """
    ns = DelNsForm(request.POST or None, instances=instances)
    if ns.is_valid():
        ns_dels = ns.cleaned_data['ns']
        for ns_del in ns_dels:
            try:
                ns_del.delete()
                messages.success(request, _("The NS record was deleted."))
            except ProtectedError:
                messages.error(
                    request,
                    (_("Error: the NS record %s can't be deleted.") % ns_del)
                )
        return redirect(reverse('machines:index-extension'))
    return form(
        {'nsform': ns, 'action_name': _("Delete")},
        'machines/machine.html',
        request
    )


@login_required
@can_create(DName)
def add_dname(request):
    """ View used to add a DName object """
    dname = DNameForm(request.POST or None)
    if dname.is_valid():
        dname.save()
        messages.success(request, _("The DNAME record was created."))
        return redirect(reverse('machines:index-extension'))
    return form(
        {'dnameform': dname, 'action_name': _("Create a DNAME record")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(DName)
def edit_dname(request, dname_instance, **_kwargs):
    """ View used to edit a DName object """
    dname = DNameForm(request.POST or None, instance=dname_instance)
    if dname.is_valid():
        if dname.changed_data:
            dname.save()
            messages.success(request, _("The DNAME record was edited."))
        return redirect(reverse('machines:index-extension'))
    return form(
        {'dnameform': dname, 'action_name': _("Edit")},
        'machines/machine.html',
        request
    )


@login_required
@can_delete_set(DName)
def del_dname(request, instances):
    """ View used to delete a DName object """
    dname = DelDNameForm(request.POST or None, instances=instances)
    if dname.is_valid():
        dname_dels = dname.cleaned_data['dname']
        for dname_del in dname_dels:
            try:
                dname_del.delete()
                messages.success(request, _("The DNAME record was deleted."))
            except ProtectedError:
                messages.error(
                    request,
                    _("Error: the DNAME record %s can't be deleted.")
                    % dname_del
                )
        return redirect(reverse('machines:index-extension'))
    return form(
        {'dnameform': dname, 'action_name': _("Delete")},
        'machines/machine.html',
        request
    )


@login_required
@can_create(Txt)
def add_txt(request):
    """ View used to add a TXT object """
    txt = TxtForm(request.POST or None)
    if txt.is_valid():
        txt.save()
        messages.success(request, _("The TXT record was created."))
        return redirect(reverse('machines:index-extension'))
    return form(
        {'txtform': txt, 'action_name': _("Create a TXT record")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(Txt)
def edit_txt(request, txt_instance, **_kwargs):
    """ View used to edit a TXT object """
    txt = TxtForm(request.POST or None, instance=txt_instance)
    if txt.is_valid():
        if txt.changed_data:
            txt.save()
            messages.success(request, _("The TXT record was edited."))
        return redirect(reverse('machines:index-extension'))
    return form(
        {'txtform': txt, 'action_name': _("Edit")},
        'machines/machine.html',
        request
    )


@login_required
@can_delete_set(Txt)
def del_txt(request, instances):
    """ View used to delete a TXT object """
    txt = DelTxtForm(request.POST or None, instances=instances)
    if txt.is_valid():
        txt_dels = txt.cleaned_data['txt']
        for txt_del in txt_dels:
            try:
                txt_del.delete()
                messages.success(request, _("The TXT record was deleted."))
            except ProtectedError:
                messages.error(
                    request,
                    (_("Error: the TXT record %s can't be deleted.") % txt_del)
                )
        return redirect(reverse('machines:index-extension'))
    return form(
        {'txtform': txt, 'action_name': _("Delete")},
        'machines/machine.html',
        request
    )


@login_required
@can_create(Srv)
def add_srv(request):
    """ View used to add a SRV object """
    srv = SrvForm(request.POST or None)
    if srv.is_valid():
        srv.save()
        messages.success(request, _("The SRV record was created."))
        return redirect(reverse('machines:index-extension'))
    return form(
        {'srvform': srv, 'action_name': _("Create an SRV record")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(Srv)
def edit_srv(request, srv_instance, **_kwargs):
    """ View used to edit a SRV object """
    srv = SrvForm(request.POST or None, instance=srv_instance)
    if srv.is_valid():
        if srv.changed_data:
            srv.save()
            messages.success(request, _("The SRV record was edited."))
        return redirect(reverse('machines:1index-extension'))
    return form(
        {'srvform': srv, 'action_name': _("Edit")},
        'machines/machine.html',
        request
    )


@login_required
@can_delete_set(Srv)
def del_srv(request, instances):
    """ View used to delete a SRV object """
    srv = DelSrvForm(request.POST or None, instances=instances)
    if srv.is_valid():
        srv_dels = srv.cleaned_data['srv']
        for srv_del in srv_dels:
            try:
                srv_del.delete()
                messages.success(request, _("The SRV record was deleted."))
            except ProtectedError:
                messages.error(
                    request,
                    (_("Error: the SRV record %s can't be deleted.") % srv_del)
                )
        return redirect(reverse('machines:index-extension'))
    return form(
        {'srvform': srv, 'action_name': _("Delete")},
        'machines/machine.html',
        request
    )


@login_required
@can_create(Domain)
@can_edit(Interface)
def add_alias(request, interface, interfaceid):
    """ View used to add an Alias object """
    alias = AliasForm(request.POST or None, user=request.user)
    if alias.is_valid():
        alias = alias.save(commit=False)
        alias.cname = interface.domain
        alias.save()
        messages.success(request, _("The alias was created."))
        return redirect(reverse(
            'machines:index-alias',
            kwargs={'interfaceid': str(interfaceid)}
        ))
    return form(
        {'aliasform': alias, 'action_name': _("Create an alias")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(Domain)
def edit_alias(request, domain_instance, **_kwargs):
    """ View used to edit an Alias object """
    alias = AliasForm(
        request.POST or None,
        instance=domain_instance,
        user=request.user
    )
    if alias.is_valid():
        if alias.changed_data:
            domain_instance = alias.save()
            messages.success(request, _("The alias was edited."))
        return redirect(reverse(
            'machines:index-alias',
            kwargs={
                'interfaceid': str(domain_instance.cname.interface_parent.id)
            }
        ))
    return form(
        {'aliasform': alias, 'action_name': _("Edit")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(Interface)
def del_alias(request, interface, interfaceid):
    """ View used to delete an Alias object """
    alias = DelAliasForm(request.POST or None, interface=interface)
    if alias.is_valid():
        alias_dels = alias.cleaned_data['alias']
        for alias_del in alias_dels:
            try:
                alias_del.delete()
                messages.success(
                    request,
                    _("The alias %s was deleted.") % alias_del
                )
            except ProtectedError:
                messages.error(
                    request,
                    (_("Error: the alias %s can't be deleted.") % alias_del)
                )
        return redirect(reverse(
            'machines:index-alias',
            kwargs={'interfaceid': str(interfaceid)}
        ))
    return form(
        {'aliasform': alias, 'action_name': _("Delete")},
        'machines/machine.html',
        request
    )


@login_required
@can_create(Role)
def add_role(request):
    """ View used to add a Role object """
    role = RoleForm(request.POST or None)
    if role.is_valid():
        role.save()
        messages.success(request, _("The role was created."))
        return redirect(reverse('machines:index-role'))
    return form(
        {'roleform': role, 'action_name': _("Create a role")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(Role)
def edit_role(request, role_instance, **_kwargs):
    """ View used to edit a Role object """
    role = RoleForm(request.POST or None, instance=role_instance)
    if role.is_valid():
        if role.changed_data:
            role.save()
            messages.success(request, _("The role was edited."))
        return redirect(reverse('machines:index-role'))
    return form(
        {'roleform': role, 'action_name': _("Edit")},
        'machines/machine.html',
        request
    )


@login_required
@can_delete_set(Role)
def del_role(request, instances):
    """ View used to delete a Service object """
    role = DelRoleForm(request.POST or None, instances=instances)
    if role.is_valid():
        role_dels = role.cleaned_data['role']
        for role_del in role_dels:
            try:
                role_del.delete()
                messages.success(request, _("The role was deleted."))
            except ProtectedError:
                messages.error(
                    request,
                    (_("Error: the role %s can't be deleted.") % role_del)
                )
        return redirect(reverse('machines:index-role'))
    return form(
        {'roleform': role, 'action_name': _("Delete")},
        'machines/machine.html',
        request
    )


@login_required
@can_create(Service)
def add_service(request):
    """ View used to add a Service object """
    service = ServiceForm(request.POST or None)
    if service.is_valid():
        service.save()
        messages.success(request, _("The service was created."))
        return redirect(reverse('machines:index-service'))
    return form(
        {'serviceform': service, 'action_name': _("Create a service")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(Service)
def edit_service(request, service_instance, **_kwargs):
    """ View used to edit a Service object """
    service = ServiceForm(request.POST or None, instance=service_instance)
    if service.is_valid():
        if service.changed_data:
            service.save()
            messages.success(request, _("The service was edited."))
        return redirect(reverse('machines:index-service'))
    return form(
        {'serviceform': service, 'action_name': _("Edit")},
        'machines/machine.html',
        request
    )


@login_required
@can_delete_set(Service)
def del_service(request, instances):
    """ View used to delete a Service object """
    service = DelServiceForm(request.POST or None, instances=instances)
    if service.is_valid():
        service_dels = service.cleaned_data['service']
        for service_del in service_dels:
            try:
                service_del.delete()
                messages.success(request, _("The service was deleted."))
            except ProtectedError:
                messages.error(
                    request,
                    (_("Error: the service %s can't be deleted.") % service_del)
                )
        return redirect(reverse('machines:index-service'))
    return form(
        {'serviceform': service, 'action_name': _("Delete")},
        'machines/machine.html',
        request
    )


@login_required
@can_edit(Service)
def regen_service(request, service, **_kwargs):
    """Ask for a regen of the service"""

    regen(service)
    return index_service(request)


@login_required
@can_view_all(Machine)
def index(request):
    """ The home view for this app. Displays the list of registered
    machines in Re2o """
    pagination_large_number = (GeneralOption
                               .get_cached_value('pagination_large_number'))
    machines_list = (Machine.objects
                     .select_related('user')
                     .prefetch_related('interface_set__domain__extension')
                     .prefetch_related('interface_set__ipv4__ip_type')
                     .prefetch_related(
        'interface_set__machine_type__ip_type__extension'
    ).prefetch_related(
        'interface_set__domain__related_domain__extension'
    ).prefetch_related('interface_set__ipv6list'))
    machines_list = SortTable.sort(
        machines_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.MACHINES_INDEX
    )
    machines_list = re2o_paginator(
        request,
        machines_list,
        pagination_large_number
    )
    return render(
        request,
        'machines/index.html',
        {'machines_list': machines_list}
    )


@login_required
@can_view_all(IpType)
def index_iptype(request):
    """ View displaying the list of existing types of IP """
    iptype_list = (IpType.objects
                   .select_related('extension')
                   .select_related('vlan')
                   .order_by('name'))
    return render(
        request,
        'machines/index_iptype.html',
        {'iptype_list': iptype_list}
    )


@login_required
@can_view_all(SOA, Mx, Ns, Txt, DName, Srv, Extension)
def index_extension(request):
    """ View displaying the list of existing extensions, the list of
    existing SOA records, the list of existing MX records , the list of
    existing NS records, the list of existing TXT records and the list of
    existing SRV records """
    extension_list = (Extension.objects
                      .select_related('origin')
                      .select_related('soa')
                      .order_by('name'))
    soa_list = SOA.objects.order_by('name')
    mx_list = (Mx.objects
               .order_by('zone')
               .select_related('zone')
               .select_related('name__extension'))
    ns_list = (Ns.objects
               .order_by('zone')
               .select_related('zone')
               .select_related('ns__extension'))
    txt_list = Txt.objects.all().select_related('zone')
    dname_list = DName.objects.all().select_related('zone')
    srv_list = (Srv.objects
                .all()
                .select_related('extension')
                .select_related('target__extension'))
    return render(
        request,
        'machines/index_extension.html',
        {
            'extension_list': extension_list,
            'soa_list': soa_list,
            'mx_list': mx_list,
            'ns_list': ns_list,
            'txt_list': txt_list,
            'dname_list': dname_list,
            'srv_list': srv_list
        }
    )


@login_required
@can_edit(Interface)
def index_alias(request, interface, interfaceid):
    """ View used to display the list of existing alias of an interface """
    alias_list = Domain.objects.filter(
        cname=Domain.objects.filter(interface_parent=interface)
    ).order_by('name')
    return render(
        request,
        'machines/index_alias.html',
        {'alias_list': alias_list, 'interface_id': interfaceid}
    )


@login_required
@can_view(Machine)
def index_sshfp(request, machine, machineid):
    """View used to display the list of existing SSHFP records associated
    with a machine"""
    sshfp_list = SshFp.objects.filter(machine=machine)
    return render(
        request,
        'machines/index_sshfp.html',
        {'sshfp_list': sshfp_list, 'machine_id': machineid}
    )


@login_required
@can_view(Interface)
def index_ipv6(request, interface, interfaceid):
    """ View used to display the list of existing IPv6 of an interface """
    ipv6_list = Ipv6List.objects.filter(interface=interface)
    return render(
        request,
        'machines/index_ipv6.html',
        {'ipv6_list': ipv6_list, 'interface_id': interfaceid}
    )


@login_required
@can_view_all(Role)
def index_role(request):
    """ View used to display the list of existing roles """
    role_list = (Role.objects
                 .prefetch_related(
        'servers__domain__extension'
    ).all())
    return render(
        request,
        'machines/index_role.html',
        {'role_list': role_list}
    )


@login_required
@can_view_all(Service)
def index_service(request):
    """ View used to display the list of existing services """
    service_list = (Service.objects
                    .prefetch_related(
        'service_link_set__server__domain__extension'
    ).all())
    servers_list = (Service_link.objects
                    .select_related('server__domain__extension')
                    .select_related('service')
                    .all())
    return render(
        request,
        'machines/index_service.html',
        {'service_list': service_list, 'servers_list': servers_list}
    )


@login_required
@can_view_all(OuverturePortList)
def index_portlist(request):
    """ View used to display the list of existing port policies """
    port_list = (OuverturePortList.objects
                 .prefetch_related('ouvertureport_set')
                 .prefetch_related('interface_set__domain__extension')
                 .prefetch_related('interface_set__machine__user')
                 .order_by('name'))
    return render(
        request,
        "machines/index_portlist.html",
        {'port_list': port_list}
    )


@login_required
@can_edit(OuverturePortList)
def edit_portlist(request, ouvertureportlist_instance, **_kwargs):
    """ View used to edit a port policy """
    port_list = EditOuverturePortListForm(
        request.POST or None,
        instance=ouvertureportlist_instance
    )
    port_formset = modelformset_factory(
        OuverturePort,
        fields=('begin', 'end', 'protocole', 'io'),
        extra=0,
        can_delete=True,
        min_num=1,
        validate_min=True,
    )(
        request.POST or None,
        queryset=ouvertureportlist_instance.ouvertureport_set.all()
    )
    if port_list.is_valid() and port_formset.is_valid():
        if port_list.changed_data:
            pl = port_list.save()
        else:
            pl = ouvertureportlist_instance
        instances = port_formset.save(commit=False)
        for to_delete in port_formset.deleted_objects:
            to_delete.delete()
        for port in instances:
            port.port_list = pl
            port.save()
        messages.success(request, _("The ports list was edited."))
        return redirect(reverse('machines:index-portlist'))
    return form(
        {'port_list': port_list, 'ports': port_formset},
        'machines/edit_portlist.html',
        request
    )


@login_required
@can_delete(OuverturePortList)
def del_portlist(request, port_list_instance, **_kwargs):
    """ View used to delete a port policy """
    port_list_instance.delete()
    messages.success(request, _("The ports list was deleted."))
    return redirect(reverse('machines:index-portlist'))


@login_required
@can_create(OuverturePortList)
def add_portlist(request):
    """ View used to add a port policy """
    port_list = EditOuverturePortListForm(request.POST or None)
    port_formset = modelformset_factory(
        OuverturePort,
        fields=('begin', 'end', 'protocole', 'io'),
        extra=0,
        can_delete=True,
        min_num=1,
        validate_min=True,
    )(request.POST or None, queryset=OuverturePort.objects.none())
    if port_list.is_valid() and port_formset.is_valid():
        pl = port_list.save()
        instances = port_formset.save(commit=False)
        for to_delete in port_formset.deleted_objects:
            to_delete.delete()
        for port in instances:
            port.port_list = pl
            port.save()
        messages.success(request, _("The ports list was created."))
        return redirect(reverse('machines:index-portlist'))
    return form(
        {'port_list': port_list, 'ports': port_formset},
        'machines/edit_portlist.html',
        request
    )


@login_required
@can_create(OuverturePort)
@can_edit(Interface)
def configure_ports(request, interface_instance, **_kwargs):
    """ View to display the list of configured port policy for an
    interface """
    if not interface_instance.may_have_port_open():
        messages.error(
            request,
            (_("Warning: the IPv4 isn't public, the opening won't have effect"
               " in v4."))
        )
    interface = EditOuverturePortConfigForm(
        request.POST or None,
        instance=interface_instance
    )
    if interface.is_valid():
        if interface.changed_data:
            interface.save()
            messages.success(request, _("The ports configuration was edited."))
        return redirect(reverse('machines:index'))
    return form(
        {'interfaceform': interface, 'action_name': _("Edit the"
                                                      " configuration")},
        'machines/machine.html',
        request
    )


# Framework Rest


class JSONResponse(HttpResponse):
    """ Class to build a JSON response. Used for API """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def mac_ip_list(_request):
    """ API view to list the active and assigned interfaces """
    interfaces = all_active_assigned_interfaces()
    seria = InterfaceSerializer(interfaces, many=True)
    return seria.data


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def full_mac_ip_list(_request):
    """ API view to list the active and assigned interfaces. More
    detailed than mac_ip_list(request) """
    interfaces = all_active_assigned_interfaces(full=True)
    seria = FullInterfaceSerializer(interfaces, many=True)
    return seria.data


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def alias(_request):
    """ API view to list the alias (CNAME) for all assigned interfaces """
    alias = (Domain.objects
             .filter(interface_parent=None)
             .filter(
        cname__in=Domain.objects.filter(
            interface_parent__in=Interface.objects.exclude(ipv4=None)
        )
    ).select_related('extension')
             .select_related('cname__extension'))
    seria = DomainSerializer(alias, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def corresp(_request):
    """ API view to list the types of IP and infos about it """
    type = IpType.objects.all().select_related('extension')
    seria = TypeSerializer(type, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def mx(_request):
    """ API view to list the MX records """
    mx = (Mx.objects.all()
          .select_related('zone')
          .select_related('name__extension'))
    seria = MxSerializer(mx, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def txt(_request):
    """ API view to list the TXT records """
    txt = Txt.objects.all().select_related('zone')
    seria = TxtSerializer(txt, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def srv(_request):
    """ API view to list the SRV records """
    srv = (Srv.objects
           .all()
           .select_related('extension')
           .select_related('target__extension'))
    seria = SrvSerializer(srv, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def ns(_request):
    """ API view to list the NS records """
    ns = (Ns.objects
          .exclude(
        ns__in=Domain.objects.filter(
            interface_parent__in=Interface.objects.filter(ipv4=None)
        )
    ).select_related('zone')
          .select_related('ns__extension'))
    seria = NsSerializer(ns, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def zones(_request):
    """ API view to list the DNS zones """
    zones = Extension.objects.all().select_related('origin')
    seria = ExtensionSerializer(zones, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def mac_ip(request):
    """ API view to list the active and assigned interfaces """
    seria = mac_ip_list(request)
    return JSONResponse(seria)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def mac_ip_dns(request):
    """ API view to list the active and assigned interfaces. More
    detailed than mac_ip_list(request) """
    seria = full_mac_ip_list(request)
    return JSONResponse(seria)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def service_servers(_request):
    """ API view to list the service links """
    service_link = (Service_link.objects
                    .all()
                    .select_related('server__domain')
                    .select_related('service'))
    seria = ServiceServersSerializer(service_link, many=True)
    return JSONResponse(seria.data)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def ouverture_ports(_request):
    """ API view to list the port policies for each IP """
    r = {'ipv4': {}, 'ipv6': {}}
    for o in (OuverturePortList.objects
            .all()
            .prefetch_related('ouvertureport_set')
            .prefetch_related('interface_set', 'interface_set__ipv4')):
        pl = {
            "tcp_in": set(map(
                str,
                o.ouvertureport_set.filter(
                    protocole=OuverturePort.TCP,
                    io=OuverturePort.IN
                )
            )),
            "tcp_out": set(map(
                str,
                o.ouvertureport_set.filter(
                    protocole=OuverturePort.TCP,
                    io=OuverturePort.OUT
                )
            )),
            "udp_in": set(map(
                str,
                o.ouvertureport_set.filter(
                    protocole=OuverturePort.UDP,
                    io=OuverturePort.IN
                )
            )),
            "udp_out": set(map(
                str,
                o.ouvertureport_set.filter(
                    protocole=OuverturePort.UDP,
                    io=OuverturePort.OUT
                )
            )),
        }
        for i in filter_active_interfaces(o.interface_set):
            if i.may_have_port_open():
                d = r['ipv4'].get(i.ipv4.ipv4, {})
                d["tcp_in"] = (d.get("tcp_in", set())
                               .union(pl["tcp_in"]))
                d["tcp_out"] = (d.get("tcp_out", set())
                                .union(pl["tcp_out"]))
                d["udp_in"] = (d.get("udp_in", set())
                               .union(pl["udp_in"]))
                d["udp_out"] = (d.get("udp_out", set())
                                .union(pl["udp_out"]))
                r['ipv4'][i.ipv4.ipv4] = d
            if i.ipv6():
                for ipv6 in i.ipv6():
                    d = r['ipv6'].get(ipv6.ipv6, {})
                    d["tcp_in"] = (d.get("tcp_in", set())
                                   .union(pl["tcp_in"]))
                    d["tcp_out"] = (d.get("tcp_out", set())
                                    .union(pl["tcp_out"]))
                    d["udp_in"] = (d.get("udp_in", set())
                                   .union(pl["udp_in"]))
                    d["udp_out"] = (d.get("udp_out", set())
                                    .union(pl["udp_out"]))
                    r['ipv6'][ipv6.ipv6] = d
    return JSONResponse(r)


@csrf_exempt
@login_required
@permission_required('machines.serveur')
def regen_achieved(request):
    """ API view to list the regen status for each (Service link, Server)
    couple """
    obj = (Service_link.objects
        .filter(
        service__in=Service.objects.filter(
            service_type=request.POST['service']
        ),
        server__in=Interface.objects.filter(
            domain__in=Domain.objects.filter(
                name=request.POST['server']
            )
        )
    ))
    if obj:
        obj.first().done_regen()
    return HttpResponse("Ok")
