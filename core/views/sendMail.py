from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, reverse
from reportlab.lib.pagesizes import A4

from django.http import JsonResponse
from core.models import Participant, Event, User
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
import qrcode


def gen_pdf(request, participant_id):
    participant = get_object_or_404(Participant, pk=participant_id)

    p = canvas.Canvas("ticket.pdf", pagesize=A4)

    p.setFont('Helvetica', 24)
    p.drawString(170, 750, "ÉVÈNEMENT " + participant.event.title)
    p.setFont('Helvetica', 14)
    p.drawString(250, 700, "Login: " + request.user.username)
    p.drawString(250, 650, "Date: " + str(participant.event.start.strftime("%b %d %Y %H:%M:%S")))

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(str(participant.event.id) + " " + str(participant.user.id))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qrcode.jpg", "JPEG")

    p.drawImage("qrcode.jpg", x=50, y=600)

    p.showPage()
    p.save()


@login_required
def send_mail(request, participant_id):
    participant = get_object_or_404(Participant, pk=participant_id)
    email = EmailMessage(
        'Billet pour l\'évènement ' + participant.event.title,
        'Bonjour, nous vous confirmons votre inscription pour l\'évènement '
        + participant.event.title + '. Vous trouverez ci-joint votre billet. Il sera a présenter'
                        'à l\'entrée de l\'évènement',
        'ticket.choisir.epita@gmail.com',
        [participant.mail],
    )
    gen_pdf(request, participant_id)
    email.attach_file("ticket.pdf")
    email.send(fail_silently=False)
    return redirect(reverse("core:event", args=[participant.event.id]))

@login_required
def mail(request):
    event_id = request.GET.get('event_id', None)
    member_id = request.GET.get('member_id', None)
    paid = request.GET.get('paid', None)
    email = request.GET.get('email', None)
    participant = Participant()
    participant.event = get_object_or_404(Event, id=event_id)
    participant.user = get_object_or_404(User, id=member_id)
    participant.paid = paid
    participant.email = email
    participant.save()
    return redirect(reverse('core:mail', args=[participant.id]))
