from django.shortcuts import render, get_object_or_404, redirect, reverse

from core.views.event import manager_check
from core.models import Event, Staff

def view(request, id):
    event = get_object_or_404(Event, id=id)
    if not manager_check(event, request.user):
        return redirect(reverse('core:event', args=[event.id]))

    staff = get_staff(event)

    variables = {}
    variables['event'] = event
    variables['staff'] = staff

    return render(request, 'event_manage.html', variables)

def get_staff(event):
    return Staff.objects.filter(event=event)
