from django.urls import path

from django.contrib.auth import views as auth_views
from core.views import index, dashboard

app_name = 'core'

urlpatterns = [
    path('', index.view, name='index'),

    # Associations
    path('association/<str:name>/', dashboard.view, name='association'),
    path('association/<str:name>/remove/<str:member>/',
        dashboard.delete_office_view, name='association_remove'),

    # Login
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, name='logout'),
]
