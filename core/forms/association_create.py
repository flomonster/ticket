from django import forms


class association_form(forms.Form):
    name = forms.CharField(label="Nom de l'association", max_length=150)
    website = forms.CharField(label="Site web", max_length=200)
    email = forms.EmailField()  # FIXME
    #logo = forms.ImageField()
