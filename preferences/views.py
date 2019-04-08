# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""
Vue d'affichage, et de modification des réglages (réglages machine,
topologie, users, service...)
"""

from __future__ import unicode_literals

from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.db import transaction
from django.utils.translation import ugettext as _

from reversion import revisions as reversion

from re2o.views import form
from re2o.acl import can_create, can_edit, can_delete_set, can_view_all, can_delete

from .forms import MailContactForm, DelMailContactForm
from .forms import (
    ServiceForm,
    ReminderForm,
    RadiusKeyForm,
    SwitchManagementCredForm,
    DocumentTemplateForm,
    DelDocumentTemplateForm
)
from .models import (
    Service,
    MailContact,
    OptionalUser,
    OptionalMachine,
    AssoOption,
    MailMessageOption,
    GeneralOption,
    OptionalTopologie,
    HomeOption,
    Reminder,
    RadiusKey,
    SwitchManagementCred,
    RadiusOption,
    CotisationsOption,
    DocumentTemplate
)
from . import models
from . import forms


@login_required
@can_view_all(OptionalUser, OptionalMachine, OptionalTopologie, GeneralOption,
              AssoOption, MailMessageOption, HomeOption)
def display_options(request):
    """Vue pour affichage des options (en vrac) classé selon les models
    correspondants dans un tableau"""
    useroptions, _created = OptionalUser.objects.get_or_create()
    machineoptions, _created = OptionalMachine.objects.get_or_create()
    topologieoptions, _created = OptionalTopologie.objects.get_or_create()
    generaloptions, _created = GeneralOption.objects.get_or_create()
    assooptions, _created = AssoOption.objects.get_or_create()
    homeoptions, _created = HomeOption.objects.get_or_create()
    mailmessageoptions, _created = MailMessageOption.objects.get_or_create()
    service_list = Service.objects.all()
    mailcontact_list = MailContact.objects.all()
    reminder_list = Reminder.objects.all()
    radiuskey_list = RadiusKey.objects.all()
    switchmanagementcred_list = SwitchManagementCred.objects.all()
    radiusoptions, _ = RadiusOption.objects.get_or_create()
    cotisationsoptions, _created = CotisationsOption.objects.get_or_create()
    document_template_list = DocumentTemplate.objects.order_by('name')
    return form({
        'useroptions': useroptions,
        'machineoptions': machineoptions,
        'topologieoptions': topologieoptions,
        'generaloptions': generaloptions,
        'assooptions': assooptions,
        'homeoptions': homeoptions,
        'mailmessageoptions': mailmessageoptions,
        'service_list': service_list,
        'mailcontact_list': mailcontact_list,
        'reminder_list': reminder_list,
        'radiuskey_list' : radiuskey_list,
        'switchmanagementcred_list': switchmanagementcred_list,
        'radiusoptions' : radiusoptions,
        'cotisationsoptions': cotisationsoptions,
        'document_template_list': document_template_list,
        }, 'preferences/display_preferences.html', request)


@login_required
def edit_options(request, section):
    """ Edition des préférences générales"""
    model = getattr(models, section, None)
    form_instance = getattr(forms, 'Edit' + section + 'Form', None)
    if not (model or form_instance):
        messages.error(request, _("Unknown object."))
        return redirect(reverse('preferences:display-options'))

    options_instance, _created = model.objects.get_or_create()
    can, msg = options_instance.can_edit(request.user)
    if not can:
        messages.error(request, msg or _("You don't have the right to edit"
                                         " this option."))
        return redirect(reverse('index'))
    options = form_instance(
        request.POST or None,
        request.FILES or None,
        instance=options_instance
    )
    if options.is_valid():
        with transaction.atomic(), reversion.create_revision():
            options.save()
            reversion.set_user(request.user)
            reversion.set_comment(
                "Field(s) edited: %s" % ', '.join(
                    field for field in options.changed_data
                )
            )
            messages.success(request, _("The preferences were edited."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {
            'options': options,
        },
        'preferences/edit_preferences.html',
        request
    )


@login_required
@can_create(Service)
def add_service(request):
    """Ajout d'un service de la page d'accueil"""
    service = ServiceForm(request.POST or None, request.FILES or None)
    if service.is_valid():
        service.save()
        messages.success(request, _("The service was added."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': service, 'action_name': _("Add a service")},
        'preferences/preferences.html',
        request
        )


@login_required
@can_edit(Service)
def edit_service(request, service_instance, **_kwargs):
    """Edition des services affichés sur la page d'accueil"""
    service = ServiceForm(
        request.POST or None,
        request.FILES or None,
        instance=service_instance
    )
    if service.is_valid():
        service.save()
        messages.success(request, _("The service was edited."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': service, 'action_name': _("Edit")},
        'preferences/preferences.html',
        request
    )

@login_required
@can_delete(Service)
def del_service(request, service_instance, **_kwargs):
    """Suppression d'un service de la page d'accueil"""
    if request.method == "POST":
        service_instance.delete()
        messages.success(request, _("The service was deleted."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'objet': service_instance, 'objet_name': 'service'},
        'preferences/delete.html',
        request
        )

@login_required
@can_create(Reminder)
def add_reminder(request):
    """Ajout d'un mail de rappel"""
    reminder = ReminderForm(request.POST or None, request.FILES or None)
    if reminder.is_valid():
        reminder.save()
        messages.success(request, _("The reminder was added."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': reminder, 'action_name': _("Add a reminder")},
        'preferences/preferences.html',
        request
        )

@login_required
@can_edit(Reminder)
def edit_reminder(request, reminder_instance, **_kwargs):
    """Edition reminder"""
    reminder = ReminderForm(
        request.POST or None,
        request.FILES or None,
        instance=reminder_instance
    )
    if reminder.is_valid():
        reminder.save()
        messages.success(request, _("The reminder was edited."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': reminder, 'action_name': _("Edit")},
        'preferences/preferences.html',
        request
    )



@login_required
@can_delete(Reminder)
def del_reminder(request, reminder_instance, **_kwargs):
    """Destruction d'un reminder"""
    if request.method == "POST":
        reminder_instance.delete()
        messages.success(request, _("The reminder was deleted."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'objet': reminder_instance, 'objet_name': 'reminder'},
        'preferences/delete.html',
        request
        )


@login_required
@can_create(RadiusKey)
def add_radiuskey(request):
    """Ajout d'une clef radius"""
    radiuskey = RadiusKeyForm(request.POST or None)
    if radiuskey.is_valid():
        radiuskey.save()
        messages.success(request, _("The RADIUS key was added."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': radiuskey, 'action_name': _("Add a RADIUS key")},
        'preferences/preferences.html',
        request
        )

@can_edit(RadiusKey)
def edit_radiuskey(request, radiuskey_instance, **_kwargs):
    """Edition des clefs radius"""
    radiuskey = RadiusKeyForm(request.POST or None, instance=radiuskey_instance)
    if radiuskey.is_valid():
        radiuskey.save()
        messages.success(request, _("The RADIUS key was edited."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': radiuskey, 'action_name': _("Edit")},
        'preferences/preferences.html',
        request
    )


@login_required
@can_delete(RadiusKey)
def del_radiuskey(request, radiuskey_instance, **_kwargs):
    """Destruction d'un radiuskey"""
    if request.method == "POST":
        try:
            radiuskey_instance.delete()
            messages.success(request, _("The RADIUS key was deleted."))
        except ProtectedError:
            messages.error(request, _("The RADIUS key is assigned to at least"
                                      " one switch, you can't delete it."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'objet': radiuskey_instance, 'objet_name': 'radiuskey'},
        'preferences/delete.html',
        request
        )


@login_required
@can_create(SwitchManagementCred)
def add_switchmanagementcred(request):
    """Ajout de creds de management"""
    switchmanagementcred = SwitchManagementCredForm(request.POST or None)
    if switchmanagementcred.is_valid():
        switchmanagementcred.save()
        messages.success(request, _("The switch management credentials were added."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': switchmanagementcred, 'action_name': _("Add switch management credentials")},
        'preferences/preferences.html',
        request
        )

@can_edit(SwitchManagementCred)
def edit_switchmanagementcred(request, switchmanagementcred_instance, **_kwargs):
    """Edition des creds de management"""
    switchmanagementcred = SwitchManagementCredForm(request.POST or None, instance=switchmanagementcred_instance)
    if switchmanagementcred.is_valid():
        switchmanagementcred.save()
        messages.success(request, _("The switch management credentials were edited."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': switchmanagementcred, 'action_name': _("Edit")},
        'preferences/preferences.html',
        request
    )


@login_required
@can_delete(SwitchManagementCred)
def del_switchmanagementcred(request, switchmanagementcred_instance, **_kwargs):
    """Destruction d'un switchmanagementcred"""
    if request.method == "POST":
        try:
            switchmanagementcred_instance.delete()
            messages.success(request, _("The switch management credentials were deleted."))
        except ProtectedError:
            messages.error(request, _("The switch management credentials are"
                                      " assigned to at least one switch, you"
                                      " can't delete them."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'objet': switchmanagementcred_instance, 'objet_name': 'switchmanagementcred'},
        'preferences/delete.html',
        request
        )


@login_required
@can_create(MailContact)
def add_mailcontact(request):
    """Add a contact email adress."""
    mailcontact = MailContactForm(
        request.POST or None,
        request.FILES or None
    )
    if mailcontact.is_valid():
        mailcontact.save()
        messages.success(request, _("The contact email address was created."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': mailcontact,
            'action_name': _("Add a contact email address")},
        'preferences/preferences.html',
        request
        )


@login_required
@can_edit(MailContact)
def edit_mailcontact(request, mailcontact_instance, **_kwargs):
    """Edit contact email adress."""
    mailcontact = MailContactForm(
        request.POST or None,
        request.FILES or None,
        instance=mailcontact_instance
    )
    if mailcontact.is_valid():
        mailcontact.save()
        messages.success(request, _("The contact email address was edited."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': mailcontact, 'action_name': _("Edit")},
        'preferences/preferences.html',
        request
    )


@login_required
@can_delete_set(MailContact)
def del_mailcontact(request, instances):
    """Delete an email adress"""
    mailcontacts = DelMailContactForm(
        request.POST or None,
        instances=instances
    )
    if mailcontacts.is_valid():
        mailcontacts_dels = mailcontacts.cleaned_data['mailcontacts']
        for mailcontacts_del in mailcontacts_dels:
            mailcontacts_del.delete()
            messages.success(request,
                    _("The contact email adress was deleted."))
        return redirect(reverse('preferences:display-options'))
    return form(
        {'preferenceform': mailcontacts, 'action_name': _("Delete")},
        'preferences/preferences.html',
        request
    )


@login_required
@can_create(DocumentTemplate)
def add_document_template(request):
    """
    View used to add a document template.
    """
    document_template = DocumentTemplateForm(
        request.POST or None,
        request.FILES or None,
    )
    if document_template.is_valid():
        document_template.save()
        messages.success(
            request,
            _("The document template was created.")
        )
        return redirect(reverse('preferences:display-options'))
    return form({
        'preferenceform': document_template,
        'action_name': _("Add"),
        'title': _("New document template")
    }, 'preferences/preferences.html', request)


@login_required
@can_edit(DocumentTemplate)
def edit_document_template(request, document_template_instance, **_kwargs):
    """
    View used to edit a document_template.
    """
    document_template = DocumentTemplateForm(
        request.POST or None,
        request.FILES or None,
        instance=document_template_instance)
    if document_template.is_valid():
        if document_template.changed_data:
            document_template.save()
            messages.success(
                request,
                _("The document template was edited.")
            )
        return redirect(reverse('preferences:display-options'))
    return form({
        'preferenceform': document_template,
        'action_name': _("Edit"),
        'title': _("Edit document template")
    }, 'preferences/preferences.html', request)


@login_required
@can_delete_set(DocumentTemplate)
def del_document_template(request, instances):
    """
    View used to delete a set of document template.
    """
    document_template = DelDocumentTemplateForm(
        request.POST or None, instances=instances)
    if document_template.is_valid():
        document_template_del = document_template.cleaned_data['document_templates']
        for document_template in document_template_del:
            try:
                document_template.delete()
                messages.success(
                    request,
                    _("The document template %(document_template)s was deleted.") % {
                        'document_template': document_template
                    }
                )
            except ProtectedError:
                messages.error(
                    request,
                    _("The document template %(document_template)s can't be deleted \
                    because it is currently being used.") % {
                        'document_template': document_template
                    }
                )
            return redirect(reverse('preferences:display-options'))
    return form({
        'preferenceform': document_template,
        'action_name': _("Delete"),
        'title': _("Delete document template")
    }, 'preferences/preferences.html', request)
