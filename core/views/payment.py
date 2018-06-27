"""@package views
This module provides a view to pay via PayPal.
"""
from core.models import Event, Participant
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from ticket.settings import PAYPAL_PRODUCTION, PAYPAL_SANDBOX


##
# @brief Display the payment page.
# @param request HTTP request.
# @param id id of the event.
# @return Rendered web page.
@login_required
def view(request, id):
    event = get_object_or_404(Event, pk=id)
    participant = Participant.objects.get(event=event, user=request.user)
    context = {
        'event': event,
        'participant': participant,
        'PAYPAL_SANDBOX': PAYPAL_SANDBOX,
        'PAYPAL_PRODUCTION': PAYPAL_PRODUCTION
    }
    print("sandbox:", PAYPAL_SANDBOX)
    return render(request, 'payment.html', context)
