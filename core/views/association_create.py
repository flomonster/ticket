from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from core.models import Association
from django.urls import reverse

from core.forms.association_create import association_form


def view(request):
    if request.method == 'POST':
        form = association_form(request.POST)
        if form.is_valid():
            association = Association()
            association.name = form.cleaned_data['name']
            association.website = form.cleaned_data['website']
            association.email = form.cleaned_data['email']
            #association.logo = form.cleaned_data['logo']
            association.save()
            return redirect(reverse('core:association', args=[association.name]))
    else:
        form = association_form()

    return render(request, 'association.html', {'form': form})
