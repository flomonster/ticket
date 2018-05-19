from django import forms

from core.models import Association, EventStatus

class event_form(forms.Form):
    title = forms.CharField(label="Nom de l'évènement", max_length=200)
    description = forms.CharField(label="Description", max_length=500, required=False)
    start = forms.DateTimeField(label="Date de début")
    end = forms.DateTimeField(label="Date de fin")
    place = forms.CharField(label="Lieu de l'évènement", max_length=200)
    cover = forms.ImageField()
    orga = forms.ModelChoiceField(queryset=Association.objects.all())
    closing = forms.DateTimeField(label="Date butoire d'inscription")
    int_capacity = forms.IntegerField(label="Capacité maximale d'internes")
    ext_capacity = forms.IntegerField(label="Capacité maximale d'externes")
    int_price = forms.IntegerField(label="Prix internes")
    ext_price = forms.IntegerField(label="Prix externes")
    display = forms.BooleanField(label="Montrer les effectifs")
    status = EventStatus.WAITING
    token = 42 #FIXME: change value later

    website = forms.CharField(label="Site web", max_length=200, required=False)
    email = forms.EmailField()
    logo = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(association_form, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
