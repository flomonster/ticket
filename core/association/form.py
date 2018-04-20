from django import forms

class AssociationForm(forms.Form):
    name = forms.charField(label = "Nom de l'association", max_length=150)
    website = forms.CharField(label="Site web", max_length=200)
    email = forms.EmailField() #FIXME
    logo = forms.ImageField()