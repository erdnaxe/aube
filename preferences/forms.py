# -*- mode: python; coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Copyright © 2017  Gabriel Détraz
# Copyright © 2017  Goulven Kermarec
# Copyright © 2017  Augustin Lemesle

"""
Formulaire d'edition des réglages : user, machine, topologie, asso...
"""

from __future__ import unicode_literals

from django.forms import ModelForm, Form
from django import forms
from django.utils.translation import ugettext_lazy as _
from re2o.mixins import FormRevMixin
from .models import (
    OptionalUser,
    OptionalMachine,
    OptionalTopologie,
    GeneralOption,
    AssoOption,
    MailMessageOption,
    HomeOption,
    Service,
    MailContact,
    Reminder,
    RadiusKey,
    SwitchManagementCred,
    RadiusOption,
    CotisationsOption,
    DocumentTemplate
)
from topologie.models import Switch


class EditOptionalUserForm(ModelForm):
    """Formulaire d'édition des options de l'user. (solde, telephone..)"""
    class Meta:
        model = OptionalUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditOptionalUserForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['is_tel_mandatory'].label = (
            _("Telephone number required")
        )
        self.fields['gpg_fingerprint'].label = _("GPG fingerprint")
        self.fields['all_can_create_club'].label = _("All can create a club")
        self.fields['all_can_create_adherent'].label = _("All can create a member")
        self.fields['self_adhesion'].label = _("Self registration")
        self.fields['shell_default'].label = _("Default shell")


class EditOptionalMachineForm(ModelForm):
    """Options machines (max de machines, etc)"""
    class Meta:
        model = OptionalMachine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditOptionalMachineForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['password_machine'].label = _("Possibility to set a"
                                                  " password per machine")
        self.fields['max_lambdauser_interfaces'].label = _("Maximum number of"
                                                           " interfaces"
                                                           " allowed for a"
                                                           " standard user")
        self.fields['max_lambdauser_aliases'].label = _("Maximum number of DNS"
                                                        " aliases allowed for"
                                                        " a standard user")
        self.fields['ipv6_mode'].label = _("IPv6 mode")
        self.fields['create_machine'].label = _("Can create a machine")


class EditOptionalTopologieForm(ModelForm):
    """Options de topologie, formulaire d'edition (vlan par default etc)
    On rajoute un champ automatic provision switchs pour gérer facilement
    l'ajout de switchs au provisionning automatique"""
    automatic_provision_switchs = forms.ModelMultipleChoiceField(
        Switch.objects.all(),
        required=False
    )

    class Meta:
        model = OptionalTopologie
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditOptionalTopologieForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )

        self.initial['automatic_provision_switchs'] = Switch.objects.filter(automatic_provision=True).order_by('interface__domain__name')

    def save(self, commit=True):
        instance = super().save(commit)
        Switch.objects.all().update(automatic_provision=False)
        self.cleaned_data['automatic_provision_switchs'].update(automatic_provision=True)
        return instance


class EditGeneralOptionForm(ModelForm):
    """Options générales (affichages de résultats de recherche, etc)"""
    class Meta:
        model = GeneralOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditGeneralOptionForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['general_message_fr'].label = _("General message in French")
        self.fields['general_message_en'].label = _("General message in English")
        self.fields['search_display_page'].label = _("Number of results"
                                                     " displayed when"
                                                     " searching")
        self.fields['pagination_number'].label = _("Number of items per page,"
                                                   " standard size (e.g."
                                                   " users)")
        self.fields['pagination_large_number'].label = _("Number of items per"
                                                         " page, large size"
                                                         " (e.g. machines)")
        self.fields['req_expire_hrs'].label = _("Time before expiration of the"
                                                " reset password link (in"
                                                " hours)")
        self.fields['site_name'].label = _("Website name")
        self.fields['email_from'].label = _("Email address for automatic"
                                            " emailing")
        self.fields['GTU_sum_up'].label = _("Summary of the General Terms of"
                                            " Use")
        self.fields['GTU'].label = _("General Terms of Use")


class EditAssoOptionForm(ModelForm):
    """Options de l'asso (addresse, telephone, etc)"""
    class Meta:
        model = AssoOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditAssoOptionForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['name'].label = _("Organisation name")
        self.fields['siret'].label = _("SIRET number")
        self.fields['adresse1'].label = _("Address (line 1)")
        self.fields['adresse2'].label = _("Address (line 2)")
        self.fields['contact'].label = _("Contact email address")
        self.fields['telephone'].label = _("Telephone number")
        self.fields['pseudo'].label = _("Usual name")
        self.fields['utilisateur_asso'].label = _("Account used for editing"
                                                  " from /admin")
        self.fields['description'].label = _("Description")


class EditMailMessageOptionForm(ModelForm):
    """Formulaire d'edition des messages de bienvenue personnalisés"""
    class Meta:
        model = MailMessageOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditMailMessageOptionForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['welcome_mail_fr'].label = _("Message for the French"
                                                 " welcome email")
        self.fields['welcome_mail_en'].label = _("Message for the English"
                                                 " welcome email")


class EditHomeOptionForm(ModelForm):
    """Edition forms of Home options"""
    class Meta:
        model = HomeOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(EditHomeOptionForm, self).__init__(
            *args,
            prefix=prefix,
            **kwargs
        )
        self.fields['facebook_url'].label = _("Facebook URL")
        self.fields['twitter_url'].label = _("Twitter URL")
        self.fields['twitter_account_name'].label = _("Twitter account name")


class EditRadiusOptionForm(ModelForm):
    """Edition forms for Radius options"""
    class Meta:
        model = RadiusOption
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        ignored=('radius_general_policy', 'vlan_decision_ok')
        fields = (
            f for f in self.fields.keys()
            if 'vlan' not in f and f not in ignored
        )
        for f in fields:
            choice = cleaned_data.get(f)
            vlan = cleaned_data.get(f+'_vlan')
            if choice == RadiusOption.SET_VLAN and vlan is None:
                self.add_error(
                    f,
                    _("You chose to set vlan but did not set any VLAN."),
                )
                self.add_error(
                    f+'_vlan',
                    _("Please, choose a VLAN."),
                )
        return cleaned_data


class EditCotisationsOptionForm(ModelForm):
    """Edition forms for Cotisations options"""
    class Meta:
        model = CotisationsOption
        fields = '__all__'


class ServiceForm(ModelForm):
    """Edition, ajout de services sur la page d'accueil"""
    class Meta:
        model = Service
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ServiceForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.fields['name'].label = _("Name")
        self.fields['url'].label = _("URL")
        self.fields['description'].label = _("Description")
        self.fields['image'].label = _("Image")


class DelServiceForm(Form):
    """Suppression de services sur la page d'accueil"""
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.none(),
        label=_("Current services"),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelServiceForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['services'].queryset = instances
        else:
            self.fields['services'].queryset = Service.objects.all()

class ReminderForm(FormRevMixin, ModelForm):
    """Edition, ajout de services sur la page d'accueil"""
    class Meta:
        model = Reminder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(ReminderForm, self).__init__(*args, prefix=prefix, **kwargs)


class RadiusKeyForm(FormRevMixin, ModelForm):
    """Edition, ajout de clef radius"""
    members = forms.ModelMultipleChoiceField(
        queryset=Switch.objects.all(),
        required=False
    )

    class Meta:
        model = RadiusKey
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(RadiusKeyForm, self).__init__(*args, prefix=prefix, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['members'] = Switch.objects.filter(radius_key=instance)

    def save(self, commit=True):
        instance = super().save(commit)
        instance.switch_set = self.cleaned_data['members']
        return instance


class SwitchManagementCredForm(FormRevMixin, ModelForm):
    """Edition, ajout de creds de management pour gestion
    et interface rest des switchs"""
    members = forms.ModelMultipleChoiceField(
        Switch.objects.all(),
        required=False
    )

    class Meta:
        model = SwitchManagementCred
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(SwitchManagementCredForm, self).__init__(*args, prefix=prefix, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['members'] = Switch.objects.filter(management_creds=instance)

    def save(self, commit=True):
        instance = super().save(commit)
        instance.switch_set = self.cleaned_data['members']
        return instance


class MailContactForm(ModelForm):
    """Edition, ajout d'adresse de contact"""
    class Meta:
        model = MailContact
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(MailContactForm, self).__init__(*args, prefix=prefix, **kwargs)


class DelMailContactForm(Form):
    """Delete contact email adress"""
    mailcontacts = forms.ModelMultipleChoiceField(
        queryset=MailContact.objects.none(),
        label=_("Current email addresses"),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelMailContactForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['mailcontacts'].queryset = instances
        else:
            self.fields['mailcontacts'].queryset = MailContact.objects.all()


class DocumentTemplateForm(FormRevMixin, ModelForm):
    """
    Form used to create a document template.
    """
    class Meta:
        model = DocumentTemplate
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', self.Meta.model.__name__)
        super(DocumentTemplateForm, self).__init__(
            *args, prefix=prefix, **kwargs)


class DelDocumentTemplateForm(FormRevMixin, Form):
    """
    Form used to delete one or more document templatess.
    The use must choose the one to delete by checking the boxes.
    """
    document_templates = forms.ModelMultipleChoiceField(
        queryset=DocumentTemplate.objects.none(),
        label=_("Available document templates"),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        instances = kwargs.pop('instances', None)
        super(DelDocumentTemplateForm, self).__init__(*args, **kwargs)
        if instances:
            self.fields['document_templates'].queryset = instances
        else:
            self.fields['document_templates'].queryset = Banque.objects.all()
