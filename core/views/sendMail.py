from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, reverse
from core.models import Participant, Event
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
import qrcode


def gen_pdf(request, participant_id):
    participant = get_object_or_404(Participant, pk=participant_id)

    p = canvas.Canvas("ticket.pdf")
    p.setFont('Helvetica', 24)
    p.drawString(100, 750, "Event: " + participant.event.title)
    p.setFont('Helvetica', 14)
    p.drawString(150, 700, "Login: " + request.user.username)
    p.drawString(150, 650, "Date: " + str(participant.event.start))

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data("lol")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("qrcode.jpg", "JPEG")

    p.drawImage("qrcode.jpg", x=150, y=500)

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
    return redirect(reverse("core:index"))
