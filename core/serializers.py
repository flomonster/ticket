from core.models import Event, Participant
from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('title', 'token', 'id')

class TicketSerializerUser(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Participant
        fields = ('event', 'user', 'used')

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ('event', 'user', 'used')
