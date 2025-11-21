from django.contrib import admin
from django.urls import path, include
from extractions import views  # your app name is 'extractions'
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User  


urlpatterns = [
    path('', views.splash_view, name='splash'),
     path('login/', views.login_view, name='login'),
     path('about/', views.about, name='about'),
    path('register/', views.register_view, name='register'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patients/', views.patient_dashboard, name='patient_dashboard'),
    path('report/', views.report, name='report'),  # ✅ New path
    path('appointments/', views.appointments, name='appointments'),
    path('staff/', views.staff_management, name='staff_management'),
    path('case-studies/', views.case_studies, name='case_studies'),
    path('doctor-schedule/', views.doctor_schedule, name='doctor_schedule'),
    path('add-patient/', views.add_patient, name='add_patient'),
    path('edit-patient/<int:id>/', views.edit_patient, name='edit_patient'),
    path('delete-patient/<int:id>/', views.delete_patient, name='delete_patient'),
    path('add-appointment/', views.add_appointment, name='add_appointment'),
    path('edit-appointment/<int:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path('delete-appointment/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('edit-staff/<int:id>/', views.edit_staff, name='edit_staff'),
    path('delete-staff/<int:id>/', views.delete_staff, name='delete_staff'),
    path('get-dashboard-counts/', views.get_dashboard_counts, name='get_dashboard_counts'),
    path('get-recent-patients/', views.get_recent_patients, name='get_recent_patients'),
    path('prescriptions/', views.prescription_form, name='prescriptions'),
    path('view_prescriptions/', views.view_prescriptions, name='view_prescriptions'),
    path('prescription/<int:pk>/pdf/', views.prescription_pdf, name='prescription_pdf'),
    path('add-case-study/', views.add_case_study, name='add_case_study'), path('edit-case-study/<int:pk>/', views.edit_case_study, name='edit_case_study'),
    path('delete-case-study/<int:pk>/', views.delete_case_study, name='delete_case_study'),
    path('add-schedule/', views.add_doctor_schedule, name='add_doctor_schedule'),
    path('edit-schedule/<int:id>/', views.edit_doctor_schedule, name='edit_doctor_schedule'),                                               
    path('delete-schedule/<int:id>/', views.delete_doctor_schedule, name='delete_doctor_schedule'),
    path('logout/', views.logout_view, name='logout'),
    path('send_chat_message/', views.send_chat_message, name='send_chat_message'),
    path('contact/', views.contact_view, name='contact'),
    path('delete/<int:id>/', views.delete_prescription, name='delete_prescription'),

]
