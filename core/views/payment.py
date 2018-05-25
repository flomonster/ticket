from core.models import Event
from django.shortcuts import render, get_object_or_404


def view(request, id):
    event = get_object_or_404(Event, pk=id)
    context = {'event': event}
    return render(request, 'payment.html', context)