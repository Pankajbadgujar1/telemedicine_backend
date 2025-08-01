from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.login_view, name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Doctor and Patient Management
    path('doctors/', views.DoctorListView.as_view(), name='doctor-list'),
    path('patients/', views.PatientListView.as_view(), name='patient-list'),
    
    # Doctor Status Management
    path('doctor/status/', views.update_doctor_status, name='update-doctor-status'),
    path('doctor/<int:doctor_id>/status/', views.get_doctor_status, name='get-doctor-status'),
    path('doctors/statuses/', views.get_all_doctor_statuses, name='get-all-doctor-statuses'),
]