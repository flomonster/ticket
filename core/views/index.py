from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth


def view(request):
    return render(request, 'index.html')

def logout(request):
    auth.logout(request)
    return render(request, 'index.html', { 'info' : "Vous étes déconnecté" })
