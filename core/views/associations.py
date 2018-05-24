from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from core.models import Association, Membership
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def view(request):
    if request.user.has_perm('core.respo'):
        assos = Association.objects.all()
    else:
        assos = get_associations(request.user)

    variables = {}
    variables['associations'] = assos
    variables['respo'] = request.user.has_perm('core.respo')
    return render(request, 'associations.html', variables)

@permission_required('core.respo')
def remove(request, name):
    Association.objects.get(name=name).delete()
    return redirect("core:associations")

def get_associations(user):
    assos = Membership.objects.filter(member__exact=user)\
                      .select_related('asso')
    assos = [p['asso'] for p in list(assos.values('asso').all())]
    return Association.objects.filter(id__in=assos)
