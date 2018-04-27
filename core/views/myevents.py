from django.shortcuts import render

from core.models import Event, EventStatus

class MyEvents:
    @staticmethod
    def view(request):
        events = MyEvents.get_events()

        # Template variables
        variables = {}
        variables['events'] = events
        variables['waiting'] = str(EventStatus.WAITING._value_)
        variables['validated'] = str(EventStatus.VALIDATED._value_)
        variables['pending'] = str(EventStatus.PENDING._value_)

        return render(request, 'my_events.html', variables)

    @staticmethod
    def get_events():
        """
        @brief get the set of events to be displayed
        @return query set of Event
        """
        # TODO: refined events query
        return Event.objects.all()