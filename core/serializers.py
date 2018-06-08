from core.models import Event
from rest_framework import serializers


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ('title', 'token', 'id')
