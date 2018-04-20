import inspect
from enum import Enum
from django.db import models
from django.contrib.auth.models import User

class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        items = inspect.getmembers(cls, lambda m : not(inspect.isroutine(m)))
        props = [m for m in items if not(m[0][:2] == '__')]
        choices = tuple([(str(p[1].value), p[0]) for p in props])
        return choices

class EventStatus(ChoiceEnum):
    """
    Defines an enum to tag an event with a status
    """
    WAITING = 1
    VALIDATED = 2
    PENDING = 3
    FINISHED = 4

class MemberRole(ChoiceEnum):
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
    logo = models.ImageField(blank=True)

    def __str__(self):
        return self.name


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
    status = models.CharField(max_length=1, choices=EventStatus.choices())
    token = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class Staff(models.Model):
    """
    An user is a staff member of an event
    """
    event = models.ForeignKey(Event, on_delete=models.DO_NOTHING)
    member = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.member.username


class Membership(models.Model):
    """
    An user is a member of an association
    """
    asso = models.ForeignKey(Association, on_delete=models.DO_NOTHING)
    member = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    role = models.CharField(max_length=1, choices=MemberRole.choices())


class Participant(models.Model):
    """
    An user has subscribed for an event
    """
    paid = models.IntegerField()
    event = models.ForeignKey(Event, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    mail = models.EmailField()
