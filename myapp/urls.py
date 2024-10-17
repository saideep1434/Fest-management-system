# urls.py

from django.urls import path
from . import views
app_name = "myapp"
urlpatterns = [
    path("",views.homepage,name = "homepage"),
    path("login/", views.login, name='login'),
    path("add_user/", views.add_user, name='add_user'),
    path('student_registration/', views.student_registration, name='student_registration'),
    path('external_registration/', views.external_registration, name='external_registration'),
    path('organiser_registration/', views.organiser_registration, name='organiser_registration'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('external/', views.external_dashboard, name='external_dashboard'),
    path('organizer/', views.organizer_dashboard, name='organizer_dashboard'),
    path('admin_event_dashboard/', views.admin_event_dashboard, name='admin_event_dashboard'),
    path('admin_url/', views.admin_dashboard, name='admin_dashboard'),
    path('event_registration/', views.event_registration, name='event_registration'),
    path('event_ext_registration/', views.event_ext_registration, name='event_ext_registration'),  
    path('accomadation_portal/', views.accomadation_portal, name='accomadation_portal'),
    path('hall_portal/', views.hall_portal, name='hall_portal'),
    path('hall_admin_portal/', views.hall_admin_portal, name='hall_admin_portal'),
    path('volunteer_registration/', views.volunteer_registration, name='volunteer_registration'), 
    #path('volunteer_reg/', views.volunteer_reg, name='volunteer_reg'), 
    path('mybooking_portal/', views.mybooking_portal, name='mybooking_portal'),
    path('logout/', views.logout_view, name='logout'),
    path('event_details/', views.event_details_org, name='event_details'),
    path('admin_event_details/', views.event_details, name='admin_event_details'),
    path('hall_details/', views.hall_details, name='hall_details'),
    path('contact.html', views.contact, name='contact'),
    path('sponsors.html', views.sponsor, name='sponsor'),
    path('winner/', views.winner, name='winner'),
    path("delete/", views.delete, name='delete'),
    #path('goBack/', views.goBack, name='goBack'),
    # Add other registration paths as needed
]
