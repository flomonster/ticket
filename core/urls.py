from django.urls import path

from django.contrib.auth import views as auth_views
from core.views import index, dashboard, association_create, associations, \
    myevents, register, payment, sendMail, event, event_create

app_name = 'core'

urlpatterns = [
    path('', index.view, name='index'),

    # Associations
    path('association/', associations.view, name='associations'),
    path('association/create/', association_create.view,
         name='association_create'),
    path('association/<str:name>/', dashboard.Dashboard.view,
         name='association'),
    path('association/<str:name>/remove/office/<str:member>/',
        dashboard.Dashboard.delete_office_view, name='association_remove'),
    path('association/remove/<str:name>/', associations.remove, name="association_rm"),
    path('association/<str:name>/confirm/event/<int:id>/',
         dashboard.Dashboard.confirm_event, name='confirm_event'),
    path('association/<str:name>/reject/event/<int:id>/',
         dashboard.Dashboard.reject_event, name='reject_event'),

    # Login
    path('login/', auth_views.login, name='login'),
    path('logout/', index.logout, name='logout'),

    # Events
    path('events/', myevents.MyEvents.view, name='my_events'),
    path('events/premium/<int:id>/', myevents.MyEvents.premium, name='premium'),
    path('events/create/', event_create.view, name='event_create'),
    path('event/<int:id>/', event.view, name='event'),
    path('event/<int:id>/remove/staff/<str:member>/',
        event.rm_staff, name="rm_staff"),

    # Register to an evenement
    path('registration/<int:id>/', register.view, name='register'),

    # Redirection to paypal button
    path('payment/<int:id>/', payment.view, name='payment'),

    # Path
    path('mail/<int:participant_id>/', sendMail.send_mail, name='mail')
]
