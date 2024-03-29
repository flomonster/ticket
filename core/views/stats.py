"""@package views
This module provides a view to display statistics.
"""
from django import forms
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import pytz

from core.models import Association, Event, Membership, MemberRole, EventStatus, Participant, Staff
import datetime as dt
from dateutil.relativedelta import relativedelta


class Constants:
    """
    Datas to compute and display statistics.
    """
    methods = {'all': 0, 'trimester': 3, 'month': 1, 'semester': 6}
    begin = dt.datetime(2018, 1, 1)
    end = None
    labels = {
        'month': [
            'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet',
            'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
        ],
        'semester': ['1er Semestre', '2e Semestre'],
        'trimester': ['Hiver', 'Printemps', 'Eté', 'Automne']
    }
    period = ''


class Period:
    """
    A period of time.
    """

    def __init__(self, name, nb):
        self.name = name
        self.nb = nb


class Stat:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
        for a in self.__dir__():
            setattr(self, a, 0)

    def calctotal(self):
        self.total = 0
        for a in dir(self):
            self.total += getattr(self, a)


class EventStat(Stat):
    def __init__(self, **kwargs):
        Stat.__init__(self, **kwargs)

    def __dir__(self):
        return ['finished', 'rejected', 'waiting', 'pending', 'validated']


class RegisterStat(Stat):
    def __init__(self, **kwargs):
        Stat.__init__(self, **kwargs)

    def __dir__(self):
        return ['ext_reg', 'ext', 'int', 'int_reg', 'staffs']


##
# @brief Compute the end date of a period.
# @param method period type (semester, trimester...)
# @param n number of the period.
def enddate(method, n):
    date = Constants.begin + relativedelta(
        months=(n * Constants.methods[method]))
    pytz.timezone(timezone.get_default_timezone_name()).localize(date)
    return date


##
# @brief Compute all the statistics of events for an association.
# @param asso Association object.
# @return EventStat object.
def assoevents(asso):
    events = Event.objects.filter(orga__exact=asso)

    if Constants.end is not None:
        events = events.filter(
            start__gt=Constants.begin, end__lt=Constants.end)

    stat = EventStat(name=asso.name)
    stat.rejected = events.filter(
        status__exact=EventStatus.REJECTED._value_).count()
    stat.finished = events.filter(
        status__exact=EventStatus.FINISHED._value_).count()
    stat.pending = events.filter(
        status__exact=EventStatus.PENDING._value_).count()
    stat.waiting = events.filter(
        status__exact=EventStatus.WAITING._value_).count()
    stat.validated = events.filter(
        status__exact=EventStatus.VALIDATED._value_).count()

    stat.calctotal()
    return stat


##
# @brief Compute event statistics for each association.
# @return List of EventStat objects.
def eventstats():
    assos = Association.objects.all().order_by('name')
    return [assoevents(asso) for asso in assos]


##
# @brief Compute statistics of registration for an event.
# @param event Event object.
# @return RegistrationStat object.
def eventregister(event):
    register = Participant.objects.filter(event__exact=event)
    staffs = Staff.objects.filter(event__exact=event)

    stat = RegisterStat(name=event.title)
    stat.int = register.filter(user__email__endswith='@epita.fr').count()
    stat.ext = register.exclude(user__email__endswith='@epita.fr').count()
    stat.ext_reg = register.exclude(user__email__endswith='@epita.fr').count()
    stat.int_reg = register.filter(user__email__endswith='@epita.fr').count()
    stat.staffs = staffs.count()
    stat.status = event.status

    stat.calctotal()
    return stat


##
# @brief Compute registration statistics for each event.
# @return List of RegisterStat.
def registerstats():
    events = Event.objects.all().order_by('start')
    if Constants.end is not None:
        events = events.filter(
            start__gt=Constants.begin, end__lt=Constants.end)

    return [eventregister(event) for event in events]


##
# @brief Return the number of intervals from the beginning to today.
# @param method type of period.
# @return int.
def allintervals(method):
    begin = Constants.begin
    i = 1
    while enddate(method, i) < dt.datetime.now():
        i += 1

    return i


def getperiods(method, no, current):
    labels = Constants.labels[method]
    t = len(labels)
    it = 0
    periods = []
    year = 2018

    for i in range(no):
        periods.append(Period(labels[it] + ' ' + str(year), i + 1))
        it += 1

        if it == t:
            year += 1
            it = 0
    Constants.period = periods[current - 1].name
    return periods


pytz.timezone(timezone.get_default_timezone_name()).localize(Constants.begin)


##
# @brief Display all statistics.
# @param request HTTP request.
# @param method type of period.
# @param no number of the period.
# @return Rendered web page.
@login_required
def view(request, method='all', no=1):
    if method != 'all':
        intervals = allintervals(method)
    else:
        Constants.period = 'Toute l\'année'

    if method != 'all':
        if not method in Constants.methods.keys() or no > intervals or no <= 0:
            return redirect(reverse('core:my_events'))

    if method != 'all':
        Constants.end = enddate(method, no)
    else:
        Constants.end = None

    event_stats = eventstats()

    variables = {}
    variables['event_stats'] = event_stats
    variables['register_stats'] = registerstats()
    variables['method'] = method
    variables['periods'] = None if method == 'all' else getperiods(
        method, intervals, no)
    variables['current'] = Constants.period

    return render(request, 'stats.html', variables)
