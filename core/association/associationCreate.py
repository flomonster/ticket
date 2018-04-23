from django.http import HttpResponse
from django.shortcuts import render

from .form import association_form


def create_association_view(request):
    if request.method == 'POST':
        form = association_form(request.POST)
        if form.is_valid():
            association = Association()
            association.name = form.cleaned_data['name']
            association.website = form.cleaned_data['website']
            association.email = form.cleaned_data['email']
            association.logo = form.cleaned_data['logo']
            association.save()
            # return HttpResponseRedirect('/thanks/')
    else:
        form = association_form()

    return render(request, 'association.html', {'form': form})
