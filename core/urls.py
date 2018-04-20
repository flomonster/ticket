from django.urls import path

from core.views import index, dashboard

app_name = 'core'

urlpatterns = [
    path('', index.view, name='index'),
    path('association/<str:name>/', dashboard.view)
]
