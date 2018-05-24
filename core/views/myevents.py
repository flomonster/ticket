from django.shortcuts import render

from core.models import Event, EventStatus, Participant

class MyEvents:
    @staticmethod
    def view(request):
        events = MyEvents.get_events(request.user)
        print(events)

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
        return Event.objects.filter(id__in=participations)
