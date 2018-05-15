from django import forms


class registration_form(forms.Form):
    mail = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(registration_form, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
