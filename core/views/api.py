from rest_framework import viewsets, generics
from django_filters.rest_framework import DjangoFilterBackend
from core.serializers import EventSerializer, TicketSerializer
from core.models import Event, Participant

class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TicketView(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = TicketSerializer
    queryset = Participant.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('event', 'user')
