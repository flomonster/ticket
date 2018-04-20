from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import *

admin.site.register(Permission)

admin.site.register(Association)
admin.site.register(Event)
admin.site.register(Staff)
admin.site.register(Membership)
admin.site.register(Participant)
