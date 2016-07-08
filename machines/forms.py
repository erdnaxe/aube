from django.forms import ModelForm, Form, ValidationError
from django import forms
from .models import Machine, Interface, MachineType

class EditMachineForm(ModelForm):
    class Meta:
        model = Machine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditMachineForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Nom de la machine'
        self.fields['type'].label = 'Type de machine'
        self.fields['type'].empty_label = "Séléctionner un type de machine"

class NewMachineForm(EditMachineForm):
    class Meta(EditMachineForm.Meta):
        fields = ['type','name']

class EditInterfaceForm(ModelForm):
    class Meta:
        model = Interface
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EditInterfaceForm, self).__init__(*args, **kwargs)
        self.fields['dns'].label = 'Nom dns de la machine'
        self.fields['mac_address'].label = 'Adresse mac'

class AddInterfaceForm(EditInterfaceForm):
    class Meta(EditInterfaceForm.Meta):
        fields = ['ipv4','mac_address','dns','details']

    def __init__(self, *args, **kwargs):
        super(AddInterfaceForm, self).__init__(*args, **kwargs)
        self.fields['ipv4'].empty_label = "Assignation automatique de l'ipv4"

class NewInterfaceForm(EditInterfaceForm):
    class Meta(EditInterfaceForm.Meta):
        fields = ['mac_address','dns','details']

class MachineTypeForm(ModelForm):
    class Meta:
        model = MachineType
        fields = ['type']

    def __init__(self, *args, **kwargs):
        super(MachineTypeForm, self).__init__(*args, **kwargs)
        self.fields['type'].label = 'Type de machine à ajouter'

class DelMachineTypeForm(ModelForm):
    machinetypes = forms.ModelMultipleChoiceField(queryset=MachineType.objects.all(), label="Types de machines actuelles",  widget=forms.CheckboxSelectMultiple)

    class Meta:
        exclude = ['type']
        model = MachineType