from django.http import HttpResponse
from django.shortcuts import render

from core.association.associationCreate import createAssociationView


def index(request):
    return HttpResponse("Acceuil")

def dashboard(request, name):
    return HttpResponse('Dashboard')

def createAssociation(request):
   return createAssociationView(request)
