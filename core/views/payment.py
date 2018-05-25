from core.models import Event
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def view(request, id):
    event = get_object_or_404(Event, pk=id)
    context = {'event': event}
    return render(request, 'payment.html', context)