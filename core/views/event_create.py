from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from core.models import Association
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from core.forms.event_create import event_form