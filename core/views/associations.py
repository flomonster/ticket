"""@package views
This module provides a view to get a list of all the associations that are
related to the currently connected user.
"""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from core.models import Association, Membership
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from rolepermissions.checkers import has_role, has_object_permission


##
# @brief List all the associations related to the currently connected user.
# @param request HTTP request
# @return Rendered web page.
@login_required
def view(request):
    if has_role(request.user, 'respo'):
        assos = Association.objects.all()
    else:
        assos = get_associations(request.user)

    variables = {}
    variables['associations'] = assos
    variables['respo'] = has_role(request.user, 'respo')
    return render(request, 'associations.html', variables)


##
# @brief Remove an association from the database.
# @param request HTTP request.
# @param name name of the association to remove.
# @return Redirection to the list of associations.
def remove(request, name):
    Association.objects.get(name=name).delete()
    return redirect("core:associations")


##
# @brief Fetch all associations related to a user.
# @param user the currently connected user.
# @return Queryset containing the related associations.
def get_associations(user):
    assos = Membership.objects.filter(member__exact=user)\
                      .select_related('asso')
    assos = [p['asso'] for p in list(assos.values('asso').all())]
    return Association.objects.filter(id__in=assos)
