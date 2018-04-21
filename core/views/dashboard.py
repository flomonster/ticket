from django.http import HttpResponse

from core.models import Association, Event


def asso_not_found(name):
    return HttpResponse('No such association ' + name)


def view(request, name):
    asso = Association.objects.filter(name=name)

    if not asso:
        return asso_not_found(name)

    asso = asso[0]

    print(related_events(asso))
    return HttpResponse('Dashboard ' + name)


def related_events(asso):
    e = Event.objects.select_related('orga').filter(orga__exact=asso)
    return e