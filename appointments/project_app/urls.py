from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    path('', views.index, name='index'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='appointment_files/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Appointments
    path('view/', views.view, name='view'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointmentsdetail'),
    path('post/new/', views.post_new, name='post_new'),
    path('appointments/<int:pk>/edit/', views.appointment_edit, name='appointment_edit'),
    path('appointments/<int:pk>/delete/', views.appoint_remove, name='appoint_remove'),
    path('appointments/<int:pk>/status/', views.update_status, name='update_status'),

    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),

    # Legacy URLs for backwards compatibility
    path('appointment/', views.appointment, name='appointment'),
    path('appointmentsdetail/<int:pk>', views.AppointmentDetailView.as_view(), name='appointmentsdetail_legacy'),
    path('view/<int:pk>/remove/', views.appoint_remove, name='appoint_remove_legacy'),
]
