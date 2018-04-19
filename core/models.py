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
