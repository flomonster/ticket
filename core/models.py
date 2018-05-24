import inspect
from enum import Enum
from django.db import models
from django.contrib.auth.models import User

class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        items = inspect.getmembers(cls, lambda m : not(inspect.isroutine(m)))
        props = [m for m in items if not(m[0][:2] == '__')]
        choices = tuple([(p[1].value, p[0]) for p in props])
        return choices

class EventStatus(ChoiceEnum):
    """
    Defines an enum to tag an event with a status
    """
    WAITING = 1
    VALIDATED = 2
    PENDING = 3
    FINISHED = 4
    REJECTED = 5

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
    logo = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start = models.DateTimeField() # Start of the event
    end = models.DateTimeField() # End of the event
    place = models.CharField(max_length=200)
    cover = models.ImageField(blank=True)
    orga = models.ForeignKey(Association, on_delete=models.CASCADE)
    closing = models.DateTimeField() # Date of subscription closing
    int_capacity = models.IntegerField() # Available tickets for members
    ext_capacity = models.IntegerField()
    int_price = models.IntegerField()
    ext_price = models.IntegerField()
    display = models.BooleanField()
    status = models.IntegerField(choices=EventStatus.choices())
    token = models.CharField(max_length=20)
    respo = models.BooleanField(default=False)
    pres = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Staff(models.Model):
    """
    An user is a staff member of an event
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.member.username


class Membership(models.Model):
    """
    An user is a member of an association
    """
    asso = models.ForeignKey(Association, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.IntegerField(choices=MemberRole.choices())

    def __str__(self):
        return self.member.username


class Participant(models.Model):
    """
    An user has subscribed for an event
    """
    paid = models.IntegerField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mail = models.EmailField()
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + ' ' + self.event.title

    def is_external(self):
        user_mail = self.user.email
        return not user_mail.endswith('epita.fr')
