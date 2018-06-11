from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from core.models import Event, EventStatus
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from core.forms.event_create import event_form
from core.models import Association

def generate_token(id):
    return str(id * 54321 % 1000000).zfill(6)


@login_required
def view(request, asso_id):
    asso = Association.objects.get(pk=asso_id)
    if request.method == 'POST':
        form = event_form(request.POST, request.FILES)
        print(request.POST)
        if form.is_valid():
            event = Event.objects.all().filter(title=form.cleaned_data['title'])
            if event.count() != 0:
                form = event_form()
                return render(request, 'event_create.html', {'form':form, 'fail': 'Evènement déjà créé'})
            evt = Event()
            evt.title = form.cleaned_data['title']
            evt.description = form.cleaned_data['description']
            evt.start = form.cleaned_data['start']
            evt.end = form.cleaned_data['end']
            evt.place = form.cleaned_data['place']
            evt.cover = form.cleaned_data['cover']
            evt.orga = asso
            evt.closing = form.cleaned_data['closing']
            evt.int_capacity = form.cleaned_data['int_capacity']
            evt.ext_capacity = form.cleaned_data['ext_capacity']
            evt.int_price = form.cleaned_data['int_price']
            evt.ext_price = form.cleaned_data['ext_price']
            evt.display = form.cleaned_data['display']
            evt.status = EventStatus.WAITING._value_
            evt.token = ''
            evt.premium = False
            evt.save()
            evt.token = generate_token(evt.id)
            evt.save()
            return redirect(reverse('core:event', args=[evt.id]))
    else:
        form = event_form()
    return render(request, 'event_create.html', {'form': form, 'asso': asso})
