from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, reverse

from core.forms.registration import registration_form
from core.models import Participant, Event, User

@login_required
def cancel(request, id):
    try:
        p = Participant.objects.get(id=id)
    except:
        return redirect(reverse('core:index'))
    p.delete()
    return redirect(reverse('core:index'))


@login_required
def view(request, id):
    event = Event.objects.all().get(pk=id)
    mail = None
    external = not request.user.email.endswith('@epita.fr')
    internals = User.objects.filter(email__endswith='@epita.fr')
    count = 0

    participants = Participant.objects.filter(event=event)
    if external:
        participants = participants.exclude(user__in=internals)
        count = event.ext_capacity
    else:
        participants = participants.filter(user__in=internals)
        count = event.int_capacity

    if participants.filter(user__exact=request.user) or participants.count() == count:
        return redirect(reverse('core:my_events'))

    if request.user.is_authenticated:
        mail = request.user.email

    if "epita" in mail:
        event_price = event.int_price
    else:
        event_price = event.ext_price

    if request.method == 'POST':
        form = registration_form(request.POST)
        if form.is_valid():
            participant = Participant()
            participant.mail = form.cleaned_data['mail']
            participant.user = request.user

            participant.paid = event_price
            participant.event = event

            if event_price == 0:
                participant.save()
                return redirect(reverse('core:mail', args=[participant.id]))

            return render(request, 'payment.html', {'form': form, 'id': id, 'event_price': event_price,
                                                     'event': event, 'participant': participant})
    else:
        form = registration_form(initial={'mail': request.user.email})

    return render(request, 'register.html', {'form': form, 'id': id, 'event_price': event_price})
