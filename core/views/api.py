"""@package views
This module provides an API to communicate with the Android application.
"""
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from core.serializers import *
from rest_framework.response import Response
from core.models import Event, Participant
from rest_framework import status

class EventViewSet(viewsets.ModelViewSet):
    """
    Class to get the list of events from the application.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TicketView(viewsets.ModelViewSet):
    """
    Class to validate the ticket of a user.
    """
    queryset = Participant.objects.all()
    serializer_class = TicketSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('event', 'user', 'id')

    def put(self, request, *args, **kwargs):
        if (not "event" in request.data or not "user" in request.data):
            return ParseError()
        used = False
        if ("used" in request.data):
            used = request.data["used"] == "true"
        event = int(request.data["event"])
        user = int(request.data["user"])
        tickets = Participant.objects.filter(event = event, user = user)
        if not tickets:
            return NotFound()
        tickets[0].used = used
        tickets[0].save()
        return Response()

class TicketViewUser(viewsets.ModelViewSet):
    """
    Class to get info of a user.
    """
    queryset = Participant.objects.all()
    serializer_class = TicketSerializerUser
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('event', 'user', 'id')
