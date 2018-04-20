from django.http import HttpResponse

from core.models import Association

def asso_not_found(name):
    return HttpResponse('No such association ' + name)

def view(request, name):
    asso = Association.objects.filter(name=name)

    if not asso:
        return asso_not_found(name)

    return HttpResponse('Dashboard ' + name)