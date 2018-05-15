from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from core.forms.registration import registration_form
from core.models import Participant, Event


@login_required
def view(request, id):
    event = Event.objects.all().get(pk=id)
    mail = None

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

            participant.save()

            participant.paid = event_price
            participant.save()

            return render(request, 'register.html', {'form': form, 'id': id, 'event_price': event_price,
                                                     'info': 'Vous êtes bien inscrit à cet évènement'})
    else:
        form = registration_form()

    return render(request, 'register.html', {'form': form, 'id': id, 'event_price': event_price})
