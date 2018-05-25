from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.models import Participant, Event
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from reportlab.pdfgen import canvas
import qrcode

@login_required
def view(request, participant_id):
    participant = get_object_or_404(Participant, pk=participant_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'
    p = canvas.Canvas(response)
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

    p.drawImage("qrcode.jpg", x = 150, y=500)

    p.showPage()
    p.save()
    return response
