from django.urls import path

from core.views import index, dashboard
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    path('', index.view, name='index'),

    # Login
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, name='logout'),

    # Associations
    path('association/<str:name>/', dashboard.view),
    path('association/<str:name>/remove/<str:member>/', dashboard.delete_office_view)

]
