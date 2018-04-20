from django.http import HttpResponse

from .form import AssociationForm

def createAssociationView(request):
    if request.method == 'POST':
        form = AssociationForm(request.POST)
        if form.is_valid():
            association = Association();
            association.name = form.cleaned_data['name']
            association.website = form.cleaned_data['website']
            association.email = form.cleaned_data['email']
            association.logo = form.cleaned_data['logo']
            association.save()
            #return HttpResponseRedirect('/thanks/')
    else:
        form = AssociationForm()

    return render(request, 'association.html', {'form' : form})