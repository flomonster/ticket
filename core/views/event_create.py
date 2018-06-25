"""@package views
This module manages the creation of an event through a view.
"""
from core.models import Event, EventStatus
from django.core.mail import EmailMessage
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from reportlab.lib.pagesizes import A4
from rolepermissions.checkers import has_role, has_object_permission

from core.forms.event_create import event_form
from core.models import Association, MemberRole


##
# @brief Generate the unique token of an event.
# @param id id of the event.
# @return int composed of 6 digits.
def generate_token(id):
    return str(id * 54321 % 1000000).zfill(6)


##
# @brief Send a mail to notify of the creation of an event.
# @param event Event object of the created event.
def notify(event):
    event = event[0]
    dests = []
    for r in User.objects.all():
        if has_role(r, 'respo'):
            dests.append(r.email)
    try:
        dests.append(
            Membership.get(
                asso=event.orga,
                role__exact=MemberRole.PRESIDENT._value_).email)
    except:
        pass

    email = EmailMessage(
        'Création de l\'évènement ' + event.title,
        'Bonjour, un évènement de l\'association ' + event.orga.name +
        ' a été créée par ' + event.creator.username +
        '. Vous pouvez le valider dès à présent.',
        'ticket.choisir.epita@gmail.com',
        dests,
    )
    email.send(fail_silently=False)


##
# @brief Render and process a form to create an event.
# @param request HTTP request.
# @param asso_id id of the association that creates the event.
# @return Rendered web page.
@login_required
def view(request, asso_id):
    asso = Association.objects.get(pk=asso_id)
    if request.method == 'POST':
        form = event_form(request.POST, request.FILES)
        if form.is_valid():
            event = Event.objects.all().filter(
                title=form.cleaned_data['title'])
            if event.count() != 0:
                form = event_form()
                return render(request, 'event_create.html', {
                    'form': form,
                    'fail': 'Evènement déjà créé'
                })
            evt = Event()
            evt.title = form.cleaned_data['title']
            evt.description = form.cleaned_data['description']

            start_date = form.cleaned_data['start_date']
            start_time = form.cleaned_data['start_time']
            evt.start = datetime.strptime(start_date + ' ' + start_time,
                                          '%Y-%m-%d %H:%M')

            end_date = form.cleaned_data['end_date']
            end_time = form.cleaned_data['end_time']
            evt.end = datetime.strptime(end_date + ' ' + end_time,
                                        '%Y-%m-%d %H:%M')

            evt.place = form.cleaned_data['place']
            evt.cover = form.cleaned_data['cover']
            evt.orga = asso

            closing_date = form.cleaned_data['closing_date']
            closing_time = form.cleaned_data['closing_time']
            evt.closing = datetime.strptime(closing_date + ' ' + closing_time,
                                            '%Y-%m-%d %H:%M')

            evt.int_capacity = form.cleaned_data['int_capacity']
            evt.ext_capacity = form.cleaned_data['ext_capacity']
            evt.int_price = form.cleaned_data['int_price']
            evt.ext_price = form.cleaned_data['ext_price']
            evt.display = form.cleaned_data['display']
            evt.status = EventStatus.WAITING._value_
            evt.token = ''
            evt.creator = request.user
            evt.premium = False
            evt.save()
            evt.token = generate_token(evt.id)
            evt.save()
            notify(event)
            return redirect(reverse('core:event', args=[evt.id]))
    else:
        form = event_form()
    return render(request, 'event_create.html', {'form': form, 'asso': asso})
