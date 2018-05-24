from django.shortcuts import render

from core.models import Event, EventStatus, Participant, Staff

class MyEvents:
    class Stat:
        registered = {}

        def __init__(self, event):
            p = Participant.objects.filter(event__exact=event)
            s = Staff.objects.filter(event__exact=event)
            externs = [e for e in p if e.is_external()]

            self.registered['externs'] = len(externs)
            self.registered['interns'] = p.count() - self.registered['externs']
            self.registered['staff'] = s.count()
            self.registered['total'] = p.count() + s.count()

    @staticmethod
    def view(request):
        events = MyEvents.get_events(request.user)
        for event in events:
            event.stat = MyEvents.Stat(event)

        # Template variables
        variables = {}
        variables['events'] = events
        variables['waiting'] = str(EventStatus.WAITING._value_)
        variables['validated'] = str(EventStatus.VALIDATED._value_)
        variables['pending'] = str(EventStatus.PENDING._value_)

        return render(request, 'my_events.html', variables)


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
