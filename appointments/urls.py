from django.urls import path
from . import views

urlpatterns = [
    # Appointment CRUD
    path('appointments/', views.AppointmentListView.as_view(), name='appointment-list'),
    path('appointments/create/', views.AppointmentCreateView.as_view(), name='appointment-create'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<int:pk>/update/', views.AppointmentUpdateView.as_view(), name='appointment-update'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment, name='appointment-cancel'),
    
    # Statistics and Reports
    path('appointments/statistics/', views.appointment_statistics, name='appointment-statistics'),
    path('doctors/<int:doctor_id>/appointments/', views.doctor_appointments, name='doctor-appointments'),
]