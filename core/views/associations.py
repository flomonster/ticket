from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from core.models import Association
from django.urls import reverse
from django.contrib.auth.decorators import login_required

@login_required
def view(request):
    return render(request, 'associations.html', {'associations': Association.objects.all()})

@login_required
def remove(request, name):
    Association.objects.get(name=name).delete()
    return redirect("core:associations")
