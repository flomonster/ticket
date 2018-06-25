"""@package views
This module provides a view to list events.
"""
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required

from core.views.event import manager_check
from core.models import Event, EventStatus, Participant, Staff, Membership, MemberRole, User
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from rolepermissions.checkers import has_role, has_object_permission, has_permission

class MyEvents:
    class Stat:
        """
        Class to represent the different statistics of an event.
        """
        def __init__(self, event):
            self.registered = {}
            self.used = {}
            self.pres = False
            self.respo = False
            p_reg = Participant.objects.filter(event__exact=event)
            p_use = Participant.objects.filter(event__exact=event).filter(used__exact=True)
            self.pres = event.pres
            self.respo = event.respo
            s = Staff.objects.filter(event__exact=event)
            self.build_row(p_reg, self.registered, s)
            self.build_row(p_use, self.used, s)


        def build_row(self, set, dict, staff):
            externs = [e for e in set if e.is_external()]

            dict['externs'] = len(externs)
            dict['interns'] = set.count() - dict['externs']
            dict['staff'] = staff.count()
            dict['total'] = set.count() + staff.count()


    class BaseForm(forms.Form):
        """
        Form to validate a ticket.
        """
        member = forms.ModelChoiceField(None)
        event = forms.ModelChoiceField(None, initial=0)

        def __init__(self, *args, **kwargs):
            super(MyEvents.BaseForm, self).__init__(*args, **kwargs)
            for field_name, field in self.fields.items():
                field.widget.attrs['class'] = 'form-control'

    @staticmethod
    @login_required
    def view(request):
        """
        @brief Display all the events related to the currently connected user.
        @param request HTTP request.
        @return Rendered web page.
        """
        memberships = Membership.objects.filter(member=request.user)

        if has_role(request.user, 'respo'):
            events = Event.objects.all()
        else:
            events = MyEvents.get_events(request.user)

        for member in memberships:
            if member.role == MemberRole.PRESIDENT._value_:
                events |= Event.objects.filter(orga=member.asso)

        if request.method == 'POST':
            form = MyEvents.BaseForm(request.POST)
            MyEvents.validate_ticket(request.POST['member'], request.POST['event'])
            return redirect(reverse('core:my_events'))

        events = events.exclude(status__exact=EventStatus.FINISHED._value_)\
                       .exclude(status__exact=EventStatus.REJECTED._value_)\
                       .order_by('start')

        for event in events:
            set = Participant.objects.filter(event=event, used=False)\
                                     .select_related('user')
            set = [p['user'] for p in list(set.values('user').all())]

            event.form = MyEvents.BaseForm()
            event.form.event = event
            event.form.fields['member'].queryset = User.objects.filter(id__in=set)
            event.form.fields['event'].queryset = Event.objects.filter(id=event.id)
            event.form.fields['event'].widget.attrs['readonly'] = True

            event.stat = MyEvents.Stat(event)
            event.disp = MyEvents.is_allowed(event, request.user)
            event.valid = has_object_permission('event_status_change', request.user, event)

        # Template variables
        variables = {}
        variables['events'] = events
        variables['waiting'] = str(EventStatus.WAITING._value_)
        variables['validated'] = str(EventStatus.VALIDATED._value_)
        variables['pending'] = str(EventStatus.PENDING._value_)
        variables['respo'] = has_role(request.user, 'respo')

        return render(request, 'my_events.html', variables)

    @staticmethod
    def is_allowed(event, user):
        """
        @brief Determine if a user can validate a ticket.
        @param event Event object.
        @param user User to check.
        @return True if the user can validate a ticket, False otherwise.
        """
        staff = Staff.objects.filter(event__exact=event)\
                             .filter(member__exact=user)
        others = Membership.objects.filter(asso=event.orga)\
                                   .filter(member__exact=user)
        return others.count() == 1 or staff.count() == 1

    @staticmethod
    def premium(request, id):
        """
        @brief Make an event premium.
        @param request HTTP request.
        @param id id of the event.
        @return Redirection to myevents.
        """
        if has_permission(request.user, 'make_premium'):
            ev = Event.objects.get(id=id)
            ev.premium = not ev.premium
            ev.save()

        return redirect(reverse('core:my_events'))

    @staticmethod
    def validate_ticket(member, event):
        """
        @brief Validate a ticket.
        @param member Member to validate.
        @param event Event object.
        """
        participant = Participant.objects.get(user=member, event=event)
        participant.used = True
        participant.save()


    @staticmethod
    def get_events(user):
        """
        @brief get the set of events to be displayed
        @return query set of Event
        """
        events = Event.objects.all()
        e = []
        for event in events:
            if manager_check(event, user):
                e.append(event.id)

        participations = Participant.objects.filter(user__exact=user)\
                                            .select_related('event')
        participations = [p['event'] for p in list(participations.values('event').all())]
        return Event.objects.filter(id__in=participations) | Event.objects.filter(id__in=e)
