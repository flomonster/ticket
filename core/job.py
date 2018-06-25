from django_cron import CronJobBase, Schedule
from django.utils import timezone

from core.models import Event, EventStatus

class Update(CronJobBase):
    """
    Class to regulary update the database
    """
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'core.update'


    def do(self):
        """
        Update status of the events according to the current date.
        """
        events = Event.objects.filter(status__exact=EventStatus.VALIDATED._value_) |\
                 Event.objects.filter(status__exact=EventStatus.PENDING._value_)
        for event in events:
            if timezone.now() > event.end:
                event.status = EventStatus.FINISHED._value_
                event.save()
            elif timezone.now() > event.start:
                event.status = EventStatus.PENDING._value_
                event.save()
