from django.http import HttpResponse


def view(request, name):
    return HttpResponse('Dashboard')