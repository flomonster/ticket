from django.db import models
from django.contrib.auth.models import User


class EventStatus:
    """
    Defines an enum to tag an event with a status
    """
    WAITING = 1
    VALIDATED = 2
    PENDING = 3
    FINISHED = 4


class MemberType:
    """
    Defines an enum to tag a membership relation
    """
    OFFICE = 1
    SIMPLE = 2
    PRESIDENT = 3


class Association(models.Model):
    name = models.CharField(max_length=150)
    website = models.CharField(max_length=200)
    email = models.EmailField()
    logo = models.ImageField()


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start = models.DateTimeField() # Start of the event
    end = models.DateTimeField() # End of the event
    place = models.CharField(max_length=200)
    cover = models.ImageField(blank=True)
    orga = models.ForeignKey(Association, on_delete=models.DO_NOTHING)
    closing = models.DateTimeField() # Date of subscription closing
    int_capacity = models.IntegerField() # Available tickets for members
    ext_capacity = models.IntegerField()
    int_price = models.IntegerField()
    ext_price = models.IntegerField()
    display = models.BooleanField()
    status = models.PositiveSmallIntegerField()
    token = models.CharField(max_length=20)


class Staff(models.Model):
    """
    An user is a staff member of an event
    """
    event = models.ForeignKey(Event, on_delete=models.DO_NOTHING)
    member = models.ForeignKey(User, on_delete=models.DO_NOTHING)


class Membership(models.Model):
    """
    An user is a member of an association
    """
    asso = models.ForeignKey(Association, on_delete=models.DO_NOTHING)
    member = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    type = models.SmallIntegerField()


class Participant(models.Model):
    """
    An user has subscribed for an event
    """
    paid = models.IntegerField()
    event = models.ForeignKey(Event, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    mail = models.EmailField()
