from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Association(models.Model):
    name = models.CharField(max_length=150)
    website = models.CharField(max_length=200)
    email = models.EmailField()
    logo = models.ImageField()
    president = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True,
                                  null=True)

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start = models.DateTimeField()
    end = models.DecimalField()
    place = models.CharField(max_length=200)
    cover = models.ImageField(blank=True)
    orga = models.ForeignKey(Association, on_delete=models.DO_NOTHING)
    closing = models.DateTimeField()
    int_capacity = models.IntegerField()
    ext_capacity = models.IntegerField()
    int_price = models.IntegerField()
    ext_price = models.IntegerField()
    display = models.BooleanField()
