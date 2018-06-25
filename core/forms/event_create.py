from django import forms
from django.forms import widgets

from core.models import Association, EventStatus

class event_form(forms.Form):
    title = forms.CharField(
            label="Nom de l'évènement", max_length=200,
            widget=forms.TextInput(attrs={'placeholder': 'Mon évènement'})
    )
    description = forms.CharField(
            label="Description",
            max_length=500,
            required=False,
            widget=widgets.Textarea(attrs={'placeholder': 'Description de l\'évènement...'})
    )
    start_date = forms.CharField(
            label="Date de début",
            widget=widgets.DateInput(attrs={'type': 'date'}),
    )
    start_time = forms.CharField(
            label="Heure de début",
            widget=widgets.TimeInput(attrs={'type': 'time'}),
    )
    end_date = forms.CharField(
            label="Date de fin",
            widget=widgets.DateInput(attrs={'type':'date'}),
    )
    end_time = forms.CharField(
            label="Heure de fin",
            widget=widgets.TimeInput(attrs={'type': 'time'}),
    )
    place = forms.CharField(
            label="Lieu de l'évènement", max_length=200,
            widget=forms.TextInput(attrs={'placeholder': 'Kremlin-Bicêtre'})
    )
    cover = forms.ImageField(
            label='Photo de couverture',
            required=False,
    )
    closing_date = forms.CharField(
            label="Date butoire d'inscription",
            widget=widgets.DateInput(attrs={'type':'date'}),
    )
    closing_time = forms.CharField(
            label="Date butoire d'inscription",
            widget=widgets.TimeInput(attrs={'type':'time'}),
    )

    int_capacity = forms.IntegerField(
            label="Capacité maximale d'internes", initial=0,
            min_value = 0
    )
    ext_capacity = forms.IntegerField(
            label="Capacité maximale d'externes", initial=0,
            min_value = 0
    )
    int_price = forms.IntegerField(
            label="Prix internes", initial=0,
            min_value = 0
    )
    ext_price = forms.IntegerField(
            label="Prix externes", initial=0,
            min_value = 0
    )
    display = forms.BooleanField(
            label="Montrer les effectifs",
            widget=widgets.CheckboxInput(attrs={'type': 'checkbox'}),
            required = False
    )

    def __init__(self, *args, **kwargs):
        super(event_form, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
