from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth

from core.models import Event
from ticket.settings import STATIC_URL


def view(request):
    events = Event.objects.all()
    return render(request, 'index.html', {"events":events, 'static_url': STATIC_URL})

def logout(request):
    auth.logout(request)
    events = Event.objects.all()
    return render(request, 'index.html', {'events':events, 'info': "Vous étes déconnecté" })
