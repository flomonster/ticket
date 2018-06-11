from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from core.serializers import *
from rest_framework.response import Response
from core.models import Event, Participant
from rest_framework import status

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
    queryset = Participant.objects.all()
    serializer_class = TicketSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('event', 'user', 'id')

class TicketViewUser(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Participant.objects.all()
    serializer_class = TicketSerializerUser
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('event', 'user', 'id')
