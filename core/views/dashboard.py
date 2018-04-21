"""@package views
This module is intended to display the dashboard of an association.

It will allow the user to manage an association through various
features.
"""
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from core.models import Association, Event


def asso_not_found(name):
    """
    @brief serve a web page to indicate that the association does not exist.
    @param name the name of the requested association.
    @return an HttpResponse serving the web page.
    """
    return HttpResponse('No such association ' + name)


def view(request, name):
    """
    @brief display the dashboard of an association if it exists.
    @param request request for the current page.
    @param name name of the requested association.
    @return an HttpResponse serving the web page.
    """
    asso = get_object_or_404(Association, name=name)

    # Creating templates variables
    variables = {}
    variables['events'] = related_events(asso)
    variables['asso'] = asso

    return HttpResponse('Dashboard ' + name)


def related_events(asso):
    """
    @brief search for the events related to an association.
    @param asso query object of the requested association.
    @return a query set of all the related events.
    """
    e = Event.objects.select_related('orga').filter(orga__exact=asso)
    return e