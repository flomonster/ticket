"""@package views
This module provides a view for the index page.
"""
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib import auth
from django.utils import timezone
import datetime
import pytz

from core.models import Event, EventStatus
from ticket.settings import STATIC_URL

def get_events():
    """
    @brief Fetch all events sorted according to premium and price.
    @return Sorted queryset of Event.
    """
    return Event.objects.all().exclude(cover='')\
                        .filter(status__exact=EventStatus.VALIDATED._value_)\
                        .order_by('-premium', '-int_price', '-ext_price')

class Entry:
    """ A calendar entry """
    def __init__(self):
        pass

def initcalendar():
    """
    @brief Create the calendar containing the events.
    @return Entry list list that represent the calendar.
    """
    L = []
    actual = timezone.now()
    allevents = Event.objects.filter(status__exact=EventStatus.VALIDATED._value_)
    d = 0

    for i in range(10):
        tmp = []
        for j in range(3):
            e = Entry()
            e.date = (actual + (d * datetime.timedelta(days=1))).date()

            start = actual + (d * datetime.timedelta(days=1))
            end = actual + ((d + 1) * datetime.timedelta(days=1))

            events = allevents.filter(start__range=(start, end))
            e.events = events
            for ev in e.events:
                ev.time = ev.start.time()

            tmp.append(e)
            d += 1

        L.append(tmp)
    return L

def view(request):
    """
    @brief Display the index page.
    @param request HTTP request.
    @return Rendered web page.
    """
    events = get_events()
    calendar = initcalendar()

    variables = {}
    variables['events'] = events
    variables['nb_events'] = range(1, events.count() + 1)
    variables['static_url'] = STATIC_URL
    variables['calendar'] = calendar
    return render(request, 'index.html', variables)

def logout(request):
    """
    @brief Logout the user and redirect to index page.
    @param request HTTP request.
    @return Redirection to index page.
    """
    auth.logout(request)
    return redirect(reverse('core:index'))
