from django import forms


class association_form(forms.Form):
    name = forms.CharField(label="Nom de l'association", max_length=150)
    website = forms.CharField(label="Site web", max_length=200, required=False)
    email = forms.EmailField()
    logo = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(association_form, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
