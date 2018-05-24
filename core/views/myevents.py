from django.shortcuts import render

from core.models import Event, EventStatus, Participant, Staff, Validation, Membership, MemberRole

class MyEvents:
    class Stat:
        registered = {}
        used = {}
        pres = False
        respo = False

        def __init__(self, event):
            p_reg = Participant.objects.filter(event__exact=event)
            p_use = Participant.objects.filter(event__exact=event).filter(used__exact=True)
            self.pres = Validation.objects.get(event__exact=event).pres
            self.respo = Validation.objects.get(event__exact=event).respo
            s = Staff.objects.filter(event__exact=event)
            self.build_row(p_reg, self.registered)
            self.build_row(p_use, self.used)


        def build_row(self, set, dict):
            externs = [e for e in set if e.is_external()]

            dict['externs'] = len(externs)
            dict['interns'] = set.count() - dict['externs']
            dict['total'] = set.count()

    @staticmethod
    def view(request):
        memberships = Membership.objects.filter(member=request.user)

        if request.user.has_perm('core.respo'):
            events = Event.objects.all()
        else:
            events = MyEvents.get_events(request.user)

        for member in memberships:
            if member.role == MemberRole.PRESIDENT._value_:
                events |= Event.objects.filter(orga=member.asso)


        for event in events:
            event.stat = MyEvents.Stat(event)
            event.disp = MyEvents.is_staff(event, request.user)
            event.valid = Membership.objects.filter(asso=event.orga)\
                                            .get(member=request.user)\
                                            .role == MemberRole.PRESIDENT._value_

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
