from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required

from core.models import Event, EventStatus, Participant, Staff, Membership, MemberRole, User
from django import forms
from django.core.exceptions import ObjectDoesNotExist

class MyEvents:
    class Stat:
        registered = {}
        used = {}
        pres = False
        respo = False

        def __init__(self, event):
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
            dict['total'] = set.count()


    class BaseForm(forms.Form):
        member = forms.ModelChoiceField(None)
        event = forms.ModelChoiceField(None, initial=0)

        def __init__(self, *args, **kwargs):
            super(MyEvents.BaseForm, self).__init__(*args, **kwargs)
            for field_name, field in self.fields.items():
                field.widget.attrs['class'] = 'form-control'

    @staticmethod
    @login_required
    def view(request):
        memberships = Membership.objects.filter(member=request.user)

        if request.user.has_perm('core.respo'):
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
            event.disp = MyEvents.is_staff(event, request.user)
            try:
                event.valid = Membership.objects.filter(asso=event.orga)\
                                                .get(member=request.user)\
                                                .role == MemberRole.PRESIDENT._value_
            except ObjectDoesNotExist:
                event.valid = False

        # Template variables
        variables = {}
        variables['events'] = events
        variables['waiting'] = str(EventStatus.WAITING._value_)
        variables['validated'] = str(EventStatus.VALIDATED._value_)
        variables['pending'] = str(EventStatus.PENDING._value_)
        variables['respo'] = request.user.has_perm('core.respo')

        return render(request, 'my_events.html', variables)

    @staticmethod
    def is_staff(event, user):
        return Staff.objects.filter(event__exact=event)\
                            .filter(member__exact=user)\
                            .count() == 1

    @staticmethod
    def premium(request, id):
        ev = Event.objects.get(id=id)
        ev.premium = not ev.premium
        ev.save()

        return redirect(reverse('core:my_events'))

    @staticmethod
    def validate_ticket(member, event):
        participant = Participant.objects.get(user=member, event=event)
        participant.used = True
        participant.save()


    @staticmethod
    def get_events(user):
        """
        @brief get the set of events to be displayed
        @return query set of Event
        """
        participations = Participant.objects.filter(user__exact=user)\
                                            .select_related('event')
        participations = [p['event'] for p in list(participations.values('event').all())]
        return Event.objects.filter(id__in=participations)\
                            .exclude(status=EventStatus.REJECTED._value_)\
                            .exclude(status=EventStatus.FINISHED._value_)
