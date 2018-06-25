"""@package views
This module provides a view to create an association.
"""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from core.models import Association
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from core.forms.association_create import association_form


@login_required
def view(request):
    """
    @brief Render and process a form to create an association.
    @param request HTTP request.
    @return Rendered web page.
    """
    if request.method == 'POST':
        form = association_form(request.POST, request.FILES)
        if form.is_valid():
            asso = Association.objects.all().filter(name=form.cleaned_data['name'])
            if asso:
                form = association_form()
                return render(request, 'association_create.html', {'form': form,
                                                                   'fail': 'Cette association a déjà été créée'})

            association = Association()
            association.name = form.cleaned_data['name']
            association.website = form.cleaned_data['website']
            association.email = form.cleaned_data['email']
            association.logo = form.cleaned_data['logo']
            association.save()
            return render(request, 'association_create.html', {'form': form,
                                                               'info': 'Votre association a bien été créée'})
    else:
        form = association_form()

    return render(request, 'association_create.html', {'form': form})
