from django import forms
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from core.models import Association, Event, Membership, MemberRole, EventStatus

class EventStat:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
        for a in self.__dir__():
            setattr(self, a, 0)

    def __dir__(self):
        return ['finished', 'rejected', 'waiting', 'pending', 'validated']

    def calctotal(self):
        self.total = 0
        for a in dir(self):
            self.total += getattr(self, a)

def assoevents(asso):
    events = Event.objects.filter(orga__exact=asso)
    stat = EventStat(name=asso.name)
    stat.rejected = events.filter(status__exact=EventStatus.REJECTED._value_).count()
    stat.finished = events.filter(status__exact=EventStatus.FINISHED._value_).count()
    stat.pending = events.filter(status__exact=EventStatus.PENDING._value_).count()
    stat.waiting = events.filter(status__exact=EventStatus.WAITING._value_).count()
    stat.validated = events.filter(status__exact=EventStatus.VALIDATED._value_).count()

    stat.calctotal()
    return stat

def eventstats():
    assos = Association.objects.all().order_by('name')
    return [assoevents(asso) for asso in assos]

@login_required
def view(request):
    event_stats = eventstats()

    variables = {}
    variables['event_stats'] = event_stats

    return render(request, 'stats.html', variables)
