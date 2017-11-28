# -*- mode: python; coding: utf-8 -*-
# Re2o est un logiciel d'administration développé initiallement au rezometz. Il
# se veut agnostique au réseau considéré, de manière à être installable en
# quelques clics.
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle
# Copyright © 2017  Maël Kervella
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# App de gestion des machines pour re2o
# Gabriel Détraz, Augustin Lemesle
# Gplv2

from __future__ import unicode_literals

from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.template.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import Context, RequestContext, loader
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import ProtectedError, F
from django.forms import ValidationError, modelformset_factory
from django.db import transaction
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from rest_framework.renderers import JSONRenderer
from machines.serializers import ( FullInterfaceSerializer,
    InterfaceSerializer,
    TypeSerializer,
    DomainSerializer,
    TxtSerializer,
    SrvSerializer,
    MxSerializer,
    ExtensionSerializer,
    ServiceServersSerializer,
    NsSerializer,
    OuverturePortsSerializer
)
from reversion import revisions as reversion
from reversion.models import Version

import re
from .forms import (
    NewMachineForm,
    EditMachineForm,
    EditInterfaceForm,
    AddInterfaceForm,
    MachineTypeForm,
    DelMachineTypeForm,
    ExtensionForm,
    DelExtensionForm,
    BaseEditInterfaceForm,
    BaseEditMachineForm
)
from .forms import (
    EditIpTypeForm,
    IpTypeForm,
    DelIpTypeForm,
    DomainForm,
    AliasForm,
    DelAliasForm,
    SOAForm,
    DelSOAForm,
    NsForm,
    DelNsForm,
    TxtForm,
    DelTxtForm,
    MxForm,
    DelMxForm,
    VlanForm,
    DelVlanForm,
    ServiceForm,
    DelServiceForm,
    NasForm,
    DelNasForm,
    SrvForm,
    DelSrvForm,
)
from .forms import EditOuverturePortListForm, EditOuverturePortConfigForm
from .models import (
    IpType,
    Machine,
    Interface,
    IpList,
    MachineType,
    Extension,
    SOA,
    Mx,
    Ns,
    Domain,
    Service,
    Service_link,
    Vlan,
    Nas,
    Txt,
    Srv,
    OuverturePortList,
    OuverturePort,
)
from users.models import User
from preferences.models import GeneralOption, OptionalMachine
from re2o.utils import (
    all_active_assigned_interfaces,
    all_has_access,
    filter_active_interfaces,
    SortTable
)
from re2o.views import form

def f_type_id( is_type_tt ):
    """ The id that will be used in HTML to store the value of the field
    type. Depends on the fact that type is generate using typeahead or not
    """
    return 'id_Interface-type_hidden' if is_type_tt else 'id_Interface-type'

def generate_ipv4_choices( form ) :
    """ Generate the parameter choices for the massive_bootstrap_form tag
    """
    f_ipv4 = form.fields['ipv4']
    used_mtype_id = []
    choices = '{"":[{key:"",value:"Choisissez d\'abord un type de machine"},'
    mtype_id = -1

    for ip in f_ipv4.queryset.annotate(mtype_id=F('ip_type__machinetype__id'))\
            .order_by('mtype_id', 'id') :
        if mtype_id != ip.mtype_id :
            mtype_id = ip.mtype_id
            used_mtype_id.append(mtype_id)
            choices += '],"{t}":[{{key:"",value:"{v}"}},'.format(
                    t = mtype_id,
                    v = f_ipv4.empty_label or '""'
            )
        choices += '{{key:{k},value:"{v}"}},'.format(
                k = ip.id,
                v = ip.ipv4
        )

    for t in form.fields['type'].queryset.exclude(id__in=used_mtype_id) :
        choices += '], "'+str(t.id)+'": ['
        choices += '{key: "", value: "' + str(f_ipv4.empty_label) + '"},'
    choices += ']}'
    return choices

def generate_ipv4_engine( is_type_tt ) :
    """ Generate the parameter engine for the massive_bootstrap_form tag
    """
    return (
        'new Bloodhound( {{'
            'datumTokenizer: Bloodhound.tokenizers.obj.whitespace( "value" ),'
            'queryTokenizer: Bloodhound.tokenizers.whitespace,'
            'local: choices_ipv4[ $( "#{type_id}" ).val() ],'
            'identify: function( obj ) {{ return obj.key; }}'
        '}} )'
        ).format(
                type_id = f_type_id( is_type_tt )
        )

def generate_ipv4_match_func( is_type_tt ) :
    """ Generate the parameter match_func for the massive_bootstrap_form tag
    """
    return (
        'function(q, sync) {{'
            'if (q === "") {{'
                'var first = choices_ipv4[$("#{type_id}").val()].slice(0, 5);'
                'first = first.map( function (obj) {{ return obj.key; }} );'
                'sync(engine_ipv4.get(first));'
            '}} else {{'
                'engine_ipv4.search(q, sync);'
            '}}'
        '}}'
        ).format(
                type_id = f_type_id( is_type_tt )
        )

def generate_ipv4_mbf_param( form, is_type_tt ):
    """ Generate all the parameters to use with the massive_bootstrap_form
    tag """
    i_choices = { 'ipv4': generate_ipv4_choices( form ) }
    i_engine = { 'ipv4': generate_ipv4_engine( is_type_tt ) }
    i_match_func = { 'ipv4': generate_ipv4_match_func( is_type_tt ) }
    i_update_on = { 'ipv4': [f_type_id( is_type_tt )] }
    i_gen_select = { 'ipv4': False }
    i_mbf_param = {
        'choices': i_choices,
        'engine': i_engine,
        'match_func': i_match_func,
        'update_on': i_update_on,
        'gen_select': i_gen_select
    }
    return i_mbf_param

@login_required
def new_machine(request, userid):
    """ Fonction de creation d'une machine. Cree l'objet machine, 
    le sous objet interface et l'objet domain à partir de model forms.
    Trop complexe, devrait être simplifié"""

    can, reason = Machine.can_create(request.user, userid)
    if not can:
        messages.error(request, reason)
        return redirect(reverse(
            'users:profil',
            kwargs={'userid':str(request.user.id)}
            ))

    # No need to check if userid exist, already done in can_create
    user = User.objects.get(pk=userid)
    machine = NewMachineForm(request.POST or None)
    interface = AddInterfaceForm(
        request.POST or None,
        infra=request.user.has_perms(('infra',))
    )
    domain = DomainForm(request.POST or None, user=user)
    if machine.is_valid() and interface.is_valid():
        new_machine = machine.save(commit=False)
        new_machine.user = user
        new_interface = interface.save(commit=False)
        domain.instance.interface_parent = new_interface
        if domain.is_valid():
            new_domain = domain.save(commit=False)
            with transaction.atomic(), reversion.create_revision():
                new_machine.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            new_interface.machine = new_machine
            with transaction.atomic(), reversion.create_revision():
                new_interface.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            new_domain.interface_parent = new_interface
            with transaction.atomic(), reversion.create_revision():
                new_domain.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            messages.success(request, "La machine a été créée")
            return redirect(reverse(
                'users:profil',
                kwargs={'userid':str(user.id)}
            ))
    i_mbf_param = generate_ipv4_mbf_param(interface, False)
    return form(
        {
            'machineform': machine,
            'interfaceform': interface,
            'domainform': domain,
            'i_mbf_param': i_mbf_param
        },
        'machines/machine.html',
        request
    )

@login_required
def edit_interface(request, interfaceid):
    """ Edition d'une interface. Distingue suivant les droits les valeurs de interfaces et machines que l'user peut modifier
    infra permet de modifier le propriétaire"""
    try:
        interface = Interface.objects.get(pk=interfaceid)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect(reverse('machines:index'))
    if not request.user.has_perms(('infra',)):
        if not request.user.has_perms(('cableur',)) and interface.machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas éditer une machine d'un autre user que vous sans droit")
            return redirect(reverse(
                'users:profil',
                kwargs={'userid':str(request.user.id)}
                ))
        machine_form = BaseEditMachineForm(request.POST or None, instance=interface.machine)
        interface_form = BaseEditInterfaceForm(request.POST or None, instance=interface, infra=False)
    else:
        machine_form = EditMachineForm(request.POST or None, instance=interface.machine)
        interface_form = EditInterfaceForm(request.POST or None, instance=interface)
    domain_form = DomainForm(request.POST or None, instance=interface.domain)
    if machine_form.is_valid() and interface_form.is_valid() and domain_form.is_valid():
        new_machine = machine_form.save(commit=False)
        new_interface = interface_form.save(commit=False)
        new_domain = domain_form.save(commit=False)
        with transaction.atomic(), reversion.create_revision():
            new_machine.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in machine_form.changed_data))
        with transaction.atomic(), reversion.create_revision():
            new_interface.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in interface_form.changed_data))
        with transaction.atomic(), reversion.create_revision():
            new_domain.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in domain_form.changed_data))
        messages.success(request, "La machine a été modifiée")
        return redirect(reverse(
            'users:profil',
            kwargs={'userid':str(interface.machine.user.id)}
            ))
    i_mbf_param = generate_ipv4_mbf_param( interface_form, False )
    return form({'machineform': machine_form, 'interfaceform': interface_form, 'domainform': domain_form, 'i_mbf_param': i_mbf_param}, 'machines/machine.html', request)

@login_required
def del_machine(request, machineid):
    """ Supprime une machine, interfaces en mode cascade"""
    try:
        machine = Machine.objects.get(pk=machineid)
    except Machine.DoesNotExist:
        messages.error(request, u"Machine inexistante" )
        return redirect(reverse('machines:index'))
    if not request.user.has_perms(('cableur',)):
        if machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas éditer une machine d'un autre user que vous sans droit")
            return redirect(reverse(
                'users:profil',
                kwargs={'userid':str(machine.user.id)}
                ))
    if request.method == "POST":
        with transaction.atomic(), reversion.create_revision():
            machine.delete()
            reversion.set_user(request.user)
        messages.success(request, "La machine a été détruite")
        return redirect(reverse(
            'users:profil',
            kwargs={'userid':str(machine.user.id)}
            ))
    return form({'objet': machine, 'objet_name': 'machine'}, 'machines/delete.html', request)

@login_required
def new_interface(request, machineid):
    """ Ajoute une interface et son domain associé à une machine existante"""
    try:
        machine = Machine.objects.get(pk=machineid)
    except Machine.DoesNotExist:
        messages.error(request, u"Machine inexistante" )
        return redirect(reverse('machines:index'))
    if not request.user.has_perms(('cableur',)):
        options, created = OptionalMachine.objects.get_or_create()
        max_lambdauser_interfaces = options.max_lambdauser_interfaces
        if machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas ajouter une interface à une machine d'un autre user que vous sans droit")
            return redirect(reverse(
                'users:profil',
                kwargs={'userid':str(request.user.id)}
                ))
        if machine.user.user_interfaces().count() >= max_lambdauser_interfaces:
            messages.error(request, "Vous avez atteint le maximum d'interfaces autorisées que vous pouvez créer vous même (%s) " % max_lambdauser_interfaces)
            return redirect(reverse(
                'users:profil',
                kwargs={'userid':str(request.user.id)}
                ))
    interface_form = AddInterfaceForm(request.POST or None, infra=request.user.has_perms(('infra',)))
    domain_form = DomainForm(request.POST or None)
    if interface_form.is_valid():
        new_interface = interface_form.save(commit=False)
        domain_form.instance.interface_parent = new_interface
        new_interface.machine = machine
        if domain_form.is_valid():
            new_domain = domain_form.save(commit=False)
            with transaction.atomic(), reversion.create_revision():
                new_interface.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            new_domain.interface_parent = new_interface
            with transaction.atomic(), reversion.create_revision():
                new_domain.save()
                reversion.set_user(request.user)
                reversion.set_comment("Création")
            messages.success(request, "L'interface a été ajoutée")
            return redirect(reverse(
                'users:profil',
                kwargs={'userid':str(machine.user.id)}
                ))
    i_mbf_param = generate_ipv4_mbf_param( interface_form, False )
    return form({'interfaceform': interface_form, 'domainform': domain_form, 'i_mbf_param': i_mbf_param}, 'machines/machine.html', request)

@login_required
def del_interface(request, interfaceid):
    """ Supprime une interface. Domain objet en mode cascade"""
    try:
        interface = Interface.objects.get(pk=interfaceid)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect(reverse('machines:index'))
    if not request.user.has_perms(('cableur',)):
        if interface.machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas éditer une machine d'un autre user que vous sans droit")
            return redirect(reverse(
                'users:profil',
                kwargs={'userid':str(request.user.id)}
                ))
    if request.method == "POST":
        machine = interface.machine
        with transaction.atomic(), reversion.create_revision():
            interface.delete()
            if not machine.interface_set.all():
               machine.delete()
            reversion.set_user(request.user)
        messages.success(request, "L'interface a été détruite")
        return redirect(reverse(
            'users:profil',
            kwargs={'userid':str(request.user.id)}
            ))
    return form({'objet': interface, 'objet_name': 'interface'}, 'machines/delete.html', request)

@login_required
@permission_required('infra')
def add_iptype(request):
    """ Ajoute un range d'ip. Intelligence dans le models, fonction views minimaliste"""
    iptype = IpTypeForm(request.POST or None)
    if iptype.is_valid():
        with transaction.atomic(), reversion.create_revision():
            iptype.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Ce type d'ip a été ajouté")
        return redirect(reverse('machines:index-iptype'))
    return form({'iptypeform': iptype}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_iptype(request, iptypeid):
    """ Edition d'un range. Ne permet pas de le redimensionner pour éviter l'incohérence"""
    try:
        iptype_instance = IpType.objects.get(pk=iptypeid)
    except IpType.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect(reverse('machines:index-iptype'))
    iptype = EditIpTypeForm(request.POST or None, instance=iptype_instance)
    if iptype.is_valid():
        with transaction.atomic(), reversion.create_revision():
            iptype.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in iptype.changed_data))
        messages.success(request, "Type d'ip modifié")
        return redirect(reverse('machines:index-iptype'))
    return form({'iptypeform': iptype}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_iptype(request):
    """ Suppression d'un range ip. Supprime les objets ip associés"""
    iptype = DelIpTypeForm(request.POST or None)
    if iptype.is_valid():
        iptype_dels = iptype.cleaned_data['iptypes']
        for iptype_del in iptype_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    iptype_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "Le type d'ip a été supprimé")
            except ProtectedError:
                messages.error(request, "Le type d'ip %s est affectée à au moins une machine, vous ne pouvez pas le supprimer" % iptype_del)
        return redirect(reverse('machines:index-iptype'))
    return form({'iptypeform': iptype}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def add_machinetype(request):
    machinetype = MachineTypeForm(request.POST or None)
    if machinetype.is_valid():
        with transaction.atomic(), reversion.create_revision():
            machinetype.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Ce type de machine a été ajouté")
        return redirect(reverse('machines:index-machinetype'))
    return form({'machinetypeform': machinetype}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_machinetype(request, machinetypeid):
    try:
        machinetype_instance = MachineType.objects.get(pk=machinetypeid)
    except MachineType.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect(reverse('machines:index-machinetype'))
    machinetype = MachineTypeForm(request.POST or None, instance=machinetype_instance)
    if machinetype.is_valid():
        with transaction.atomic(), reversion.create_revision():
            machinetype.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in machinetype.changed_data))
        messages.success(request, "Type de machine modifié")
        return redirect(reverse('machines:index-machinetype'))
    return form({'machinetypeform': machinetype}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_machinetype(request):
    machinetype = DelMachineTypeForm(request.POST or None)
    if machinetype.is_valid():
        machinetype_dels = machinetype.cleaned_data['machinetypes']
        for machinetype_del in machinetype_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    machinetype_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "Le type de machine a été supprimé")
            except ProtectedError:
                messages.error(request, "Le type de machine %s est affectée à au moins une machine, vous ne pouvez pas le supprimer" % machinetype_del)
        return redirect(reverse('machines:index-machinetype'))
    return form({'machinetypeform': machinetype}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def add_extension(request):
    extension = ExtensionForm(request.POST or None)
    if extension.is_valid():
        with transaction.atomic(), reversion.create_revision():
            extension.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cette extension a été ajoutée")
        return redirect(reverse('machines:index-extension'))
    return form({'extensionform': extension}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_extension(request, extensionid):
    try:
        extension_instance = Extension.objects.get(pk=extensionid)
    except Extension.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect(reverse('machines:index-extension'))
    extension = ExtensionForm(request.POST or None, instance=extension_instance)
    if extension.is_valid():
        with transaction.atomic(), reversion.create_revision():
            extension.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in extension.changed_data))
        messages.success(request, "Extension modifiée")
        return redirect(reverse('machines:index-extension'))
    return form({'extensionform': extension}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_extension(request):
    extension = DelExtensionForm(request.POST or None)
    if extension.is_valid():
        extension_dels = extension.cleaned_data['extensions']
        for extension_del in extension_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    extension_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "L'extension a été supprimée")
            except ProtectedError:
                messages.error(request, "L'extension %s est affectée à au moins un type de machine, vous ne pouvez pas la supprimer" % extension_del)
        return redirect(reverse('machines:index-extension'))
    return form({'extensionform': extension}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def add_soa(request):
    soa = SOAForm(request.POST or None)
    if soa.is_valid():
        with transaction.atomic(), reversion.create_revision():
            soa.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet enregistrement SOA a été ajouté")
        return redirect(reverse('machines:index-extension'))
    return form({'soaform': soa}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_soa(request, soaid):
    try:
        soa_instance = SOA.objects.get(pk=soaid)
    except SOA.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect(reverse('machines:index-extension'))
    soa = SOAForm(request.POST or None, instance=soa_instance)
    if soa.is_valid():
        with transaction.atomic(), reversion.create_revision():
            soa.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in soa.changed_data))
        messages.success(request, "SOA modifié")
        return redirect(reverse('machines:index-extension'))
    return form({'soaform': soa}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_soa(request):
    soa = DelSOAForm(request.POST or None)
    if soa.is_valid():
        soa_dels = soa.cleaned_data['soa']
        for soa_del in soa_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    soa_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "Le SOA a été supprimée")
            except ProtectedError:
                messages.error(request, "Erreur le SOA suivant %s ne peut être supprimé" % soa_del)
        return redirect(reverse('machines:index-extension'))
    return form({'soaform': soa}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def add_mx(request):
    mx = MxForm(request.POST or None)
    if mx.is_valid():
        with transaction.atomic(), reversion.create_revision():
            mx.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet enregistrement mx a été ajouté")
        return redirect(reverse('machines:index-extension'))
    return form({'mxform': mx}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_mx(request, mxid):
    try:
        mx_instance = Mx.objects.get(pk=mxid)
    except Mx.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect(reverse('machines:index-extension'))
    mx = MxForm(request.POST or None, instance=mx_instance)
    if mx.is_valid():
        with transaction.atomic(), reversion.create_revision():
            mx.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in mx.changed_data))
        messages.success(request, "Mx modifié")
        return redirect(reverse('machines:index-extension'))
    return form({'mxform': mx}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_mx(request):
    mx = DelMxForm(request.POST or None)
    if mx.is_valid():
        mx_dels = mx.cleaned_data['mx']
        for mx_del in mx_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    mx_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "L'mx a été supprimée")
            except ProtectedError:
                messages.error(request, "Erreur le Mx suivant %s ne peut être supprimé" % mx_del)
        return redirect(reverse('machines:index-extension'))
    return form({'mxform': mx}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def add_ns(request):
    ns = NsForm(request.POST or None)
    if ns.is_valid():
        with transaction.atomic(), reversion.create_revision():
            ns.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet enregistrement ns a été ajouté")
        return redirect(reverse('machines:index-extension'))
    return form({'nsform': ns}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_ns(request, nsid):
    try:
        ns_instance = Ns.objects.get(pk=nsid)
    except Ns.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect(reverse('machines:index-extension'))
    ns = NsForm(request.POST or None, instance=ns_instance)
    if ns.is_valid():
        with transaction.atomic(), reversion.create_revision():
            ns.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in ns.changed_data))
        messages.success(request, "Ns modifié")
        return redirect(reverse('machines:index-extension'))
    return form({'nsform': ns}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_ns(request):
    ns = DelNsForm(request.POST or None)
    if ns.is_valid():
        ns_dels = ns.cleaned_data['ns']
        for ns_del in ns_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    ns_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "Le ns a été supprimée")
            except ProtectedError:
                messages.error(request, "Erreur le Ns suivant %s ne peut être supprimé" % ns_del)
        return redirect(reverse('machines:index-extension'))
    return form({'nsform': ns}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def add_txt(request):
    txt = TxtForm(request.POST or None)
    if txt.is_valid():
        with transaction.atomic(), reversion.create_revision():
            txt.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet enregistrement text a été ajouté")
        return redirect(reverse('machines:index-extension'))
    return form({'txtform': txt}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_txt(request, txtid):
    try:
        txt_instance = Txt.objects.get(pk=txtid)
    except Txt.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect(reverse('machines:index-extension'))
    txt = TxtForm(request.POST or None, instance=txt_instance)
    if txt.is_valid():
        with transaction.atomic(), reversion.create_revision():
            txt.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in txt.changed_data))
        messages.success(request, "Txt modifié")
        return redirect(reverse('machines:index-extension'))
    return form({'txtform': txt}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_txt(request):
    txt = DelTxtForm(request.POST or None)
    if txt.is_valid():
        txt_dels = txt.cleaned_data['txt']
        for txt_del in txt_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    txt_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "Le txt a été supprimé")
            except ProtectedError:
                messages.error(request, "Erreur le Txt suivant %s ne peut être supprimé" % txt_del)
        return redirect(reverse('machines:index-extension'))
    return form({'txtform': txt}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def add_srv(request):
    srv = SrvForm(request.POST or None)
    if srv.is_valid():
        with transaction.atomic(), reversion.create_revision():
            srv.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet enregistrement srv a été ajouté")
        return redirect(reverse('machines:index-extension'))
    return form({'srvform': srv}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_srv(request, srvid):
    try:
        srv_instance = Srv.objects.get(pk=srvid)
    except Srv.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect(reverse('machines:index-extension'))
    srv = SrvForm(request.POST or None, instance=srv_instance)
    if srv.is_valid():
        with transaction.atomic(), reversion.create_revision():
            srv.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in srv.changed_data))
        messages.success(request, "Srv modifié")
        return redirect(reverse('machines:index-extension'))
    return form({'srvform': srv}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_srv(request):
    srv = DelSrvForm(request.POST or None)
    if srv.is_valid():
        srv_dels = srv.cleaned_data['srv']
        for srv_del in srv_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    srv_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "L'srv a été supprimée")
            except ProtectedError:
                messages.error(request, "Erreur le Srv suivant %s ne peut être supprimé" % srv_del)
        return redirect(reverse('machines:index-extension'))
    return form({'srvform': srv}, 'machines/machine.html', request)

@login_required
def add_alias(request, interfaceid):
    try:
        interface = Interface.objects.get(pk=interfaceid)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect(reverse('machines:index'))
    if not request.user.has_perms(('cableur',)):
        options, created = OptionalMachine.objects.get_or_create()
        max_lambdauser_aliases = options.max_lambdauser_aliases
        if interface.machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas ajouter un alias à une machine d'un autre user que vous sans droit")
            return redirect(reverse(
                'users:profil',
                kwargs={'userid':str(request.user.id)}
                ))
        if Domain.objects.filter(cname__in=Domain.objects.filter(interface_parent__in=interface.machine.user.user_interfaces())).count() >= max_lambdauser_aliases:
            messages.error(request, "Vous avez atteint le maximum d'alias autorisées que vous pouvez créer vous même (%s) " % max_lambdauser_aliases)
            return redirect(reverse(
                'users:profil',
                kwargs={'userid':str(request.user.id)}
                ))
    alias = AliasForm(request.POST or None, infra=request.user.has_perms(('infra',)))
    if alias.is_valid():
        alias = alias.save(commit=False)
        alias.cname = interface.domain
        with transaction.atomic(), reversion.create_revision():
            alias.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet alias a été ajouté")
        return redirect(reverse(
            'machines:index-alias', 
            kwargs={'interfaceid':str(interfaceid)}
            ))
    return form({'aliasform': alias}, 'machines/machine.html', request)

@login_required
def edit_alias(request, aliasid):
    try:
        alias_instance = Domain.objects.get(pk=aliasid)
    except Domain.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect(reverse('machines:index-extension'))
    if not request.user.has_perms(('cableur',)) and alias_instance.cname.interface_parent.machine.user != request.user:
        messages.error(request, "Vous ne pouvez pas ajouter un alias à une machine d'un autre user que vous sans droit")
        return redirect(reverse(
            'users:profil',
            kwargs={'userid':str(request.user.id)}
            ))
    alias = AliasForm(request.POST or None, instance=alias_instance, infra=request.user.has_perms(('infra',)))
    if alias.is_valid():
        with transaction.atomic(), reversion.create_revision():
            alias_instance = alias.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in alias.changed_data))
        messages.success(request, "Alias modifié")
        return redirect(reverse(
            'machines:index-alias', 
            kwargs={'interfaceid':str(alias_instance.cname.interface_parent.id)}
            ))
    return form({'aliasform': alias}, 'machines/machine.html', request)

@login_required
def del_alias(request, interfaceid):
    try:
        interface = Interface.objects.get(pk=interfaceid)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect(reverse('machines:index'))
    if not request.user.has_perms(('cableur',)) and interface.machine.user != request.user:
        messages.error(request, "Vous ne pouvez pas ajouter un alias à une machine d'un autre user que vous sans droit")
        return redirect(reverse(
            'users:profil',
            kwargs={'userid':str(request.user.id)}
            ))
    alias = DelAliasForm(request.POST or None, interface=interface)
    if alias.is_valid():
        alias_dels = alias.cleaned_data['alias']
        for alias_del in alias_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    alias_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "L'alias %s a été supprimé" % alias_del)
            except ProtectedError:
                messages.error(request, "Erreur l'alias suivant %s ne peut être supprimé" % alias_del)
        return redirect(reverse(
            'machines:index-alias', 
            kwargs={'interfaceid':str(interfaceid)}
            ))
    return form({'aliasform': alias}, 'machines/machine.html', request)


@login_required
@permission_required('infra')
def add_service(request):
    service = ServiceForm(request.POST or None)
    if service.is_valid():
        with transaction.atomic(), reversion.create_revision():
            service.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet enregistrement service a été ajouté")
        return redirect(reverse('machines:index-service'))
    return form({'serviceform': service}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_service(request, serviceid):
    try:
        service_instance = Service.objects.get(pk=serviceid)
    except Ns.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect(reverse('machines:index-extension'))
    service = ServiceForm(request.POST or None, instance=service_instance)
    if service.is_valid():
        with transaction.atomic(), reversion.create_revision():
            service.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in service.changed_data))
        messages.success(request, "Service modifié")
        return redirect(reverse('machines:index-service'))
    return form({'serviceform': service}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_service(request):
    service = DelServiceForm(request.POST or None)
    if service.is_valid():
        service_dels = service.cleaned_data['service']
        for service_del in service_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    service_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "Le service a été supprimée")
            except ProtectedError:
                messages.error(request, "Erreur le service suivant %s ne peut être supprimé" % service_del)
        return redirect(reverse('machines:index-service'))
    return form({'serviceform': service}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def add_vlan(request):
    vlan = VlanForm(request.POST or None)
    if vlan.is_valid():
        with transaction.atomic(), reversion.create_revision():
            vlan.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet enregistrement vlan a été ajouté")
        return redirect(reverse('machines:index-vlan'))
    return form({'vlanform': vlan}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_vlan(request, vlanid):
    try:
        vlan_instance = Vlan.objects.get(pk=vlanid)
    except Vlan.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect(reverse('machines:index-vlan'))
    vlan = VlanForm(request.POST or None, instance=vlan_instance)
    if vlan.is_valid():
        with transaction.atomic(), reversion.create_revision():
            vlan.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in vlan.changed_data))
        messages.success(request, "Vlan modifié")
        return redirect(reverse('machines:index-vlan'))
    return form({'vlanform': vlan}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_vlan(request):
    vlan = DelVlanForm(request.POST or None)
    if vlan.is_valid():
        vlan_dels = vlan.cleaned_data['vlan']
        for vlan_del in vlan_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    vlan_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "Le vlan a été supprimée")
            except ProtectedError:
                messages.error(request, "Erreur le Vlan suivant %s ne peut être supprimé" % vlan_del)
        return redirect(reverse('machines:index-vlan'))
    return form({'vlanform': vlan}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def add_nas(request):
    nas = NasForm(request.POST or None)
    if nas.is_valid():
        with transaction.atomic(), reversion.create_revision():
            nas.save()
            reversion.set_user(request.user)
            reversion.set_comment("Création")
        messages.success(request, "Cet enregistrement nas a été ajouté")
        return redirect(reverse('machines:index-nas'))
    return form({'nasform': nas}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def edit_nas(request, nasid):
    try:
        nas_instance = Nas.objects.get(pk=nasid)
    except Nas.DoesNotExist:
        messages.error(request, u"Entrée inexistante" )
        return redirect(reverse('machines:index-nas'))
    nas = NasForm(request.POST or None, instance=nas_instance)
    if nas.is_valid():
        with transaction.atomic(), reversion.create_revision():
            nas.save()
            reversion.set_user(request.user)
            reversion.set_comment("Champs modifié(s) : %s" % ', '.join(field for field in nas.changed_data))
        messages.success(request, "Nas modifié")
        return redirect(reverse('machines:index-nas'))
    return form({'nasform': nas}, 'machines/machine.html', request)

@login_required
@permission_required('infra')
def del_nas(request):
    nas = DelNasForm(request.POST or None)
    if nas.is_valid():
        nas_dels = nas.cleaned_data['nas']
        for nas_del in nas_dels:
            try:
                with transaction.atomic(), reversion.create_revision():
                    nas_del.delete()
                    reversion.set_user(request.user)
                messages.success(request, "Le nas a été supprimé")
            except ProtectedError:
                messages.error(request, "Erreur le Nas suivant %s ne peut être supprimé" % nas_del)
        return redirect(reverse('machines:index-nas'))
    return form({'nasform': nas}, 'machines/machine.html', request)

@login_required
@permission_required('cableur')
def index(request):
    options, created = GeneralOption.objects.get_or_create()
    pagination_large_number = options.pagination_large_number
    machines_list = Machine.objects.select_related('user').prefetch_related('interface_set__domain__extension').prefetch_related('interface_set__ipv4__ip_type').prefetch_related('interface_set__type__ip_type__extension').prefetch_related('interface_set__domain__related_domain__extension')
    machines_list = SortTable.sort(
        machines_list,
        request.GET.get('col'),
        request.GET.get('order'),
        SortTable.MACHINES_INDEX
    )
    paginator = Paginator(machines_list, pagination_large_number)
    page = request.GET.get('page')
    try:
        machines_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        machines_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        machines_list = paginator.page(paginator.num_pages)
    return render(request, 'machines/index.html', {'machines_list': machines_list})

@login_required
@permission_required('cableur')
def index_iptype(request):
    iptype_list = IpType.objects.select_related('extension').select_related('vlan').order_by('type')
    return render(request, 'machines/index_iptype.html', {'iptype_list':iptype_list})

@login_required
@permission_required('cableur')
def index_vlan(request):
    vlan_list = Vlan.objects.prefetch_related('iptype_set').order_by('vlan_id')
    return render(request, 'machines/index_vlan.html', {'vlan_list':vlan_list})

@login_required
@permission_required('cableur')
def index_machinetype(request):
    machinetype_list = MachineType.objects.select_related('ip_type').order_by('type')
    return render(request, 'machines/index_machinetype.html', {'machinetype_list':machinetype_list})

@login_required
@permission_required('cableur')
def index_nas(request):
    nas_list = Nas.objects.select_related('machine_type').select_related('nas_type').order_by('name')
    return render(request, 'machines/index_nas.html', {'nas_list':nas_list})

@login_required
@permission_required('cableur')
def index_extension(request):
    extension_list = Extension.objects.select_related('origin').select_related('soa').order_by('name')
    soa_list = SOA.objects.order_by('name')
    mx_list = Mx.objects.order_by('zone').select_related('zone').select_related('name__extension')
    ns_list = Ns.objects.order_by('zone').select_related('zone').select_related('ns__extension')
    txt_list = Txt.objects.all().select_related('zone')
    srv_list = Srv.objects.all().select_related('extension').select_related('target__extension')
    return render(request, 'machines/index_extension.html', {'extension_list':extension_list, 'soa_list': soa_list, 'mx_list': mx_list, 'ns_list': ns_list, 'txt_list' : txt_list, 'srv_list': srv_list})

@login_required
def index_alias(request, interfaceid):
    try:
        interface = Interface.objects.get(pk=interfaceid)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect(reverse('machines:index'))
    if not request.user.has_perms(('cableur',)) and interface.machine.user != request.user:
        messages.error(request, "Vous ne pouvez pas éditer une machine d'un autre user que vous sans droit")
        return redirect(reverse(
            'users:profil',
            kwargs={'userid':str(request.user.id)}
            ))
    alias_list = Domain.objects.filter(cname=Domain.objects.filter(interface_parent=interface)).order_by('name')
    return render(request, 'machines/index_alias.html', {'alias_list':alias_list, 'interface_id': interfaceid})

@login_required
@permission_required('cableur')
def index_service(request):
    service_list = Service.objects.prefetch_related('service_link_set__server__domain__extension').all()
    servers_list = Service_link.objects.select_related('server__domain__extension').select_related('service').all()
    return render(request, 'machines/index_service.html', {'service_list':service_list, 'servers_list':servers_list})

@login_required
def history(request, object, id):
    if object == 'machine':
        try:
            object_instance = Machine.objects.get(pk=id)
        except Machine.DoesNotExist:
            messages.error(request, "Machine inexistante")
            return redirect(reverse('machines:index'))
        if not request.user.has_perms(('cableur',)) and object_instance.user != request.user:
            messages.error(request, "Vous ne pouvez pas afficher l'historique d'une machine d'un autre user que vous sans droit cableur")
            return redirect(reverse(
                'users:profil',
                kwargs={'userid':str(request.user.id)}
                ))
    elif object == 'interface':
        try:
            object_instance = Interface.objects.get(pk=id)
        except Interface.DoesNotExist:
            messages.error(request, "Interface inexistante")
            return redirect(reverse('machines:index'))
        if not request.user.has_perms(('cableur',)) and object_instance.machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas afficher l'historique d'une interface d'un autre user que vous sans droit cableur")
            return redirect(reverse(
                'users:profil',
                kwargs={'userid':str(request.user.id)}
                ))
    elif object == 'alias':
        try:
            object_instance = Domain.objects.get(pk=id)
        except Domain.DoesNotExist:
            messages.error(request, "Alias inexistant")
            return redirect(reverse('machines:index'))
        if not request.user.has_perms(('cableur',)) and object_instance.cname.interface_parent.machine.user != request.user:
            messages.error(request, "Vous ne pouvez pas afficher l'historique d'un alias d'un autre user que vous sans droit cableur")
            return redirect(reverse(
                'users:profil',
                kwargs={'userid':str(request.user.id)}
                ))
    elif object == 'machinetype' and request.user.has_perms(('cableur',)):
        try:
             object_instance = MachineType.objects.get(pk=id)
        except MachineType.DoesNotExist:
             messages.error(request, "Type de machine inexistant")
             return redirect(reverse('machines:index'))
    elif object == 'iptype' and request.user.has_perms(('cableur',)):
        try:
             object_instance = IpType.objects.get(pk=id)
        except IpType.DoesNotExist:
             messages.error(request, "Type d'ip inexistant")
             return redirect(reverse('machines:index'))
    elif object == 'extension' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Extension.objects.get(pk=id)
        except Extension.DoesNotExist:
             messages.error(request, "Extension inexistante")
             return redirect(reverse('machines:index'))
    elif object == 'soa' and request.user.has_perms(('cableur',)):
        try:
             object_instance = SOA.objects.get(pk=id)
        except SOA.DoesNotExist:
             messages.error(request, "SOA inexistant")
             return redirect(reverse('machines:index'))
    elif object == 'mx' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Mx.objects.get(pk=id)
        except Mx.DoesNotExist:
             messages.error(request, "Mx inexistant")
             return redirect(reverse('machines:index'))
    elif object == 'txt' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Txt.objects.get(pk=id)
        except Txt.DoesNotExist:
             messages.error(request, "Txt inexistant")
             return redirect(reverse('machines:index'))
    elif object == 'srv' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Srv.objects.get(pk=id)
        except Srv.DoesNotExist:
             messages.error(request, "Srv inexistant")
             return redirect(reverse('machines:index'))
    elif object == 'ns' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Ns.objects.get(pk=id)
        except Ns.DoesNotExist:
             messages.error(request, "Ns inexistant")
             return redirect(reverse('machines:index'))
    elif object == 'service' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Service.objects.get(pk=id)
        except Service.DoesNotExist:
             messages.error(request, "Service inexistant")
             return redirect(reverse('machines:index'))
    elif object == 'vlan' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Vlan.objects.get(pk=id)
        except Vlan.DoesNotExist:
             messages.error(request, "Vlan inexistant")
             return redirect(reverse('machines:index'))
    elif object == 'nas' and request.user.has_perms(('cableur',)):
        try:
             object_instance = Nas.objects.get(pk=id)
        except Nas.DoesNotExist:
             messages.error(request, "Nas inexistant")
             return redirect(reverse('machines:index'))
    else:
        messages.error(request, "Objet  inconnu")
        return redirect(reverse('machines:index'))
    options, created = GeneralOption.objects.get_or_create()
    pagination_number = options.pagination_number
    reversions = Version.objects.get_for_object(object_instance)
    paginator = Paginator(reversions, pagination_number)
    page = request.GET.get('page')
    try:
        reversions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reversions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reversions = paginator.page(paginator.num_pages)
    return render(request, 're2o/history.html', {'reversions': reversions, 'object': object_instance})


@login_required
@permission_required('cableur')
def index_portlist(request):
    port_list = OuverturePortList.objects.prefetch_related('ouvertureport_set')\
    .prefetch_related('interface_set__domain__extension')\
    .prefetch_related('interface_set__machine__user').order_by('name')
    return render(request, "machines/index_portlist.html", {'port_list':port_list})

@login_required
@permission_required('bureau')
def edit_portlist(request, pk):
    try:
        port_list_instance = OuverturePortList.objects.get(pk=pk)
    except OuverturePortList.DoesNotExist:
        messages.error(request, "Liste de ports inexistante")
        return redirect(reverse('machines:index-portlist'))
    port_list = EditOuverturePortListForm(request.POST or None, instance=port_list_instance)
    port_formset = modelformset_factory(
            OuverturePort,
            fields=('begin','end','protocole','io'),
            extra=0,
            can_delete=True,
	    min_num=1,
	    validate_min=True,
    )(request.POST or None, queryset=port_list_instance.ouvertureport_set.all())
    if port_list.is_valid() and port_formset.is_valid():
        pl = port_list.save()
        instances = port_formset.save(commit=False)
        for to_delete in port_formset.deleted_objects:
            to_delete.delete()
        for port in instances:
            port.port_list = pl
            port.save()
        messages.success(request, "Liste de ports modifiée")
        return redirect(reverse('machines:index-portlist'))
    return form({'port_list' : port_list, 'ports' : port_formset}, 'machines/edit_portlist.html', request)

@login_required
@permission_required('bureau')
def del_portlist(request, pk):
    try:
        port_list_instance = OuverturePortList.objects.get(pk=pk)
    except OuverturePortList.DoesNotExist:
        messages.error(request, "Liste de ports inexistante")
        return redirect(reverse('machines:index-portlist'))
    if port_list_instance.interface_set.all():
        messages.error(request, "Cette liste de ports est utilisée")
        return redirect(reverse('machines:index-portlist'))
    port_list_instance.delete()
    messages.success(request, "La liste de ports a été supprimée")
    return redirect(reverse('machines:index-portlist'))

@login_required
@permission_required('bureau')
def add_portlist(request):
    port_list = EditOuverturePortListForm(request.POST or None)
    port_formset = modelformset_factory(
            OuverturePort,
            fields=('begin','end','protocole','io'),
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
        messages.success(request, "Liste de ports créée")
        return redirect(reverse('machines:index-portlist'))
    return form({'port_list' : port_list, 'ports' : port_formset}, 'machines/edit_portlist.html', request)
    port_list = EditOuverturePortListForm(request.POST or None)
    if port_list.is_valid():
        port_list.save()
        messages.success(request, "Liste de ports créée")
        return redirect(reverse('machines:index-portlist'))
    return form({'machineform' : port_list}, 'machines/machine.html', request)

@login_required
@permission_required('cableur')
def configure_ports(request, pk):
    try:
        interface_instance = Interface.objects.get(pk=pk)
    except Interface.DoesNotExist:
        messages.error(request, u"Interface inexistante" )
        return redirect(reverse('machines:index'))
    if not interface_instance.may_have_port_open():
        messages.error(request, "Attention, l'ipv4 n'est pas publique, l'ouverture n'aura pas d'effet en v4")
    interface = EditOuverturePortConfigForm(request.POST or None, instance=interface_instance)
    if interface.is_valid():
        interface.save()
        messages.success(request, "Configuration des ports mise à jour.")
        return redirect(reverse('machines:index'))
    return form({'interfaceform' : interface}, 'machines/machine.html', request)

""" Framework Rest """

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
@login_required
@permission_required('serveur')
def mac_ip_list(request):
    interfaces = all_active_assigned_interfaces()
    seria = InterfaceSerializer(interfaces, many=True)
    return seria.data

@csrf_exempt
@login_required
@permission_required('serveur')
def full_mac_ip_list(request):
    interfaces = all_active_assigned_interfaces()
    seria = FullInterfaceSerializer(interfaces, many=True)
    return seria.data

@csrf_exempt
@login_required
@permission_required('serveur')
def alias(request):
    alias = Domain.objects.filter(interface_parent=None).filter(cname__in=Domain.objects.filter(interface_parent__in=Interface.objects.exclude(ipv4=None))).select_related('extension').select_related('cname__extension')
    seria = DomainSerializer(alias, many=True)
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def corresp(request):
    type = IpType.objects.all().select_related('extension')
    seria = TypeSerializer(type, many=True)
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def mx(request):
    mx = Mx.objects.all().select_related('zone').select_related('name__extension')
    seria = MxSerializer(mx, many=True)
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def txt(request):
    txt = Txt.objects.all().select_related('zone')
    seria = TxtSerializer(txt, many=True)
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def srv(request):
    srv = Srv.objects.all().select_related('extension').select_related('target__extension')
    seria = SrvSerializer(srv, many=True)
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def ns(request):
    ns = Ns.objects.exclude(ns__in=Domain.objects.filter(interface_parent__in=Interface.objects.filter(ipv4=None))).select_related('zone').select_related('ns__extension')
    seria = NsSerializer(ns, many=True)
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def zones(request):
    zones = Extension.objects.all().select_related('origin')
    seria = ExtensionSerializer(zones, many=True)
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def mac_ip(request):
    seria = mac_ip_list(request)
    return JSONResponse(seria)

@csrf_exempt
@login_required
@permission_required('serveur')
def mac_ip_dns(request):
    seria = full_mac_ip_list(request)
    return JSONResponse(seria)

@csrf_exempt
@login_required
@permission_required('serveur')
def service_servers(request):
    service_link = Service_link.objects.all().select_related('server__domain').select_related('service')
    seria = ServiceServersSerializer(service_link, many=True)
    return JSONResponse(seria.data)

@csrf_exempt
@login_required
@permission_required('serveur')
def ouverture_ports(request):
    r = {'ipv4':{}, 'ipv6':{}}
    for o in OuverturePortList.objects.all().prefetch_related('ouvertureport_set').prefetch_related('interface_set', 'interface_set__ipv4'):
        pl = {
            "tcp_in":set(map(str,o.ouvertureport_set.filter(protocole=OuverturePort.TCP, io=OuverturePort.IN))),
            "tcp_out":set(map(str,o.ouvertureport_set.filter(protocole=OuverturePort.TCP, io=OuverturePort.OUT))),
            "udp_in":set(map(str,o.ouvertureport_set.filter(protocole=OuverturePort.UDP, io=OuverturePort.IN))),
            "udp_out":set(map(str,o.ouvertureport_set.filter(protocole=OuverturePort.UDP, io=OuverturePort.OUT))),
        }
        for i in filter_active_interfaces(o.interface_set):
            if i.may_have_port_open():
                d = r['ipv4'].get(i.ipv4.ipv4, {})
                d["tcp_in"] = d.get("tcp_in",set()).union(pl["tcp_in"])
                d["tcp_out"] = d.get("tcp_out",set()).union(pl["tcp_out"])
                d["udp_in"] = d.get("udp_in",set()).union(pl["udp_in"])
                d["udp_out"] = d.get("udp_out",set()).union(pl["udp_out"])
                r['ipv4'][i.ipv4.ipv4] = d
            if i.ipv6_object:
                d = r['ipv6'].get(i.ipv6, {})
                d["tcp_in"] = d.get("tcp_in",set()).union(pl["tcp_in"])
                d["tcp_out"] = d.get("tcp_out",set()).union(pl["tcp_out"])
                d["udp_in"] = d.get("udp_in",set()).union(pl["udp_in"])
                d["udp_out"] = d.get("udp_out",set()).union(pl["udp_out"])
                r['ipv6'][i.ipv6] = d
    return JSONResponse(r)
@csrf_exempt
@login_required
@permission_required('serveur')
def regen_achieved(request):
    obj = Service_link.objects.filter(service__in=Service.objects.filter(service_type=request.POST['service']), server__in=Interface.objects.filter(domain__in=Domain.objects.filter(name=request.POST['server'])))
    if obj:
        obj.first().done_regen()
    return HttpResponse("Ok")

