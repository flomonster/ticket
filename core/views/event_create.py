from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from core.models import Event
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from core.forms.event_create import event_form


@login_required
def view(request):
    if request.method == 'POST':
        form = event_form(request.POST, request.FILES)
        if form.is_valid():
            event = Event.objects.all().filter(title=form.cleaned_data['title'])
            if event:
                form = event_form()
                return render(request, 'event_create.html', {'form':form, 'fail': 'Evènement déjà créé'})
            evt = Event()
            evt.title = form.cleaned_data['title']
            evt.description = form.cleaned_data['description']
            evt.start = form.cleaned_data['start']
            evt.end = form.cleaned_data['end']
            evt.place = form.cleaned_data['place']
            evt.cover = form.cleaned_data['cover']
            evt.orga = form.cleaned_data['orga']
            evt.closing = form.cleaned_data['closing']
            evt.int_capacity = form.cleaned_data['int_capacity']
            evt.ext_capacity = form.cleaned_data['ext_capacity']
            evt.int_price = form.cleaned_data['int_price']
            evt.ext_price = form.cleaned_data['ext_price']
            evt.display = form.cleaned_data['display']
            evt.status = form.cleaned_data['status']
            evt.token = form.cleaned_data['token']
            evt.save()
            return render(request, 'event_create.html', {'form':form, 'info': 'Evènement créé'})
    else:
        form = event_form()
    return render(request, 'event_create.html', {'form': form})