from django import forms
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from core.models import Association, Event, Membership, MemberRole, EventStatus


@login_required
def view(request):
    return render(request, 'stats.html', {})
