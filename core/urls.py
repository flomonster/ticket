from django.urls import path

from django.contrib.auth import views as auth_views
from core.views import index, dashboard, association_create, associations

app_name = 'core'

urlpatterns = [
    path('', index.view, name='index'),

    # Associations
    path('association/', associations.view, name='associations'),
    path('association/create/', association_create.view, name='association_create'),
    path('association/<str:name>/', dashboard.Dashboard.view, name='association'),
    path('association/<str:name>/remove/office/<str:member>/',
        dashboard.Dashboard.delete_office_view, name='association_remove'),
    path('association/remove/<str:name>/', associations.remove, name="association_rm"),

    # Login
    path('login/', auth_views.login, name='login'),
    path('logout/', index.logout, name='logout'),
]
