from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from core.models import Association
from django.urls import reverse

def view(request):
    return render(request, 'associations.html', {'associations': Association.objects.all()})
