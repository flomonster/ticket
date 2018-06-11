from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth

from core.models import Event, EventStatus
from ticket.settings import STATIC_URL

def get_events():
    return Event.objects.all().exclude(cover='')\
                        .filter(status__exact=EventStatus.VALIDATED._value_)\
                        .order_by('-premium', '-int_price', '-ext_price')

def view(request):
    events = get_events()
    return render(request, 'index.html', {"events":events, "nb_events": range(1, events.count() + 1), 'static_url': STATIC_URL})

def logout(request):
    auth.logout(request)
    events = get_events()
    return render(request, 'index.html', {'events':events, 'info': "Vous étes déconnecté" })
