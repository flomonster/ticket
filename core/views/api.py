from rest_framework import viewsets
from core.serializers import EventSerializer
from core.models import Event

class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
