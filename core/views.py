from django.http import HttpResponse
from django.shortcuts import render

from core.association.associationCreate import createAssociationView


def index(request):
    return HttpResponse("Acceuil")

def createAssociation(request):
   return createAssociationView(request)