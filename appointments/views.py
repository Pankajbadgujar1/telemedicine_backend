from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Appointment
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentListSerializer,
    AppointmentDetailSerializer,
    AppointmentUpdateSerializer
)

class AppointmentCreateView(generics.CreateAPIView):
    serializer_class = AppointmentCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Ensure only patients can create appointments
        if self.request.user.role != 'patient':
            raise permissions.PermissionDenied("Only patients can create appointments.")
        serializer.save(patient=self.request.user)

class AppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related('patient', 'doctor')
        
        if user.role == 'patient':
            # Patients can only see their own appointments
            queryset = queryset.filter(patient=user)
        elif user.role == 'doctor':
            # Doctors can see their appointments
            queryset = queryset.filter(doctor=user)
        else:
            # Admin can see all appointments
            pass
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-appointment_date')

class AppointmentDetailView(generics.RetrieveAPIView):
    serializer_class = AppointmentDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related('patient', 'doctor')
        
        if user.role == 'patient':
            return queryset.filter(patient=user)
        elif user.role == 'doctor':
            return queryset.filter(doctor=user)
        
        return queryset

class AppointmentUpdateView(generics.UpdateAPIView):
    serializer_class = AppointmentUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.select_related('patient', 'doctor')
        
        if user.role == 'patient':
            # Patients can only update their own appointments
            return queryset.filter(patient=user)
        elif user.role == 'doctor':
            # Doctors can update appointments assigned to them
            return queryset.filter(doctor=user)
        
        return queryset

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, appointment_id):
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Check permissions
        if request.user.role == 'patient' and appointment.patient != request.user:
            return Response(
                {'error': 'You can only cancel your own appointments.'},
                status=status.HTTP_403_FORBIDDEN
            )
        elif request.user.role == 'doctor' and appointment.doctor != request.user:
            return Response(
                {'error': 'You can only cancel appointments assigned to you.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if appointment can be cancelled
        if appointment.status in ['completed', 'cancelled']:
            return Response(
                {'error': f'Cannot cancel {appointment.status} appointment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'cancelled'
        appointment.save()
        
        return Response(
            {'message': 'Appointment cancelled successfully.'},
            status=status.HTTP_200_OK
        )
        
    except Appointment.DoesNotExist:
        return Response(
            {'error': 'Appointment not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_statistics(request):
    user = self.request.user
    
    if user.role == 'patient':
        appointments = Appointment.objects.filter(patient=user)
    elif user.role == 'doctor':
        appointments = Appointment.objects.filter(doctor=user)
    else:
        appointments = Appointment.objects.all()
    
    stats = {
        'total': appointments.count(),
        'pending': appointments.filter(status='pending').count(),
        'confirmed': appointments.filter(status='confirmed').count(),
        'completed': appointments.filter(status='completed').count(),
        'cancelled': appointments.filter(status='cancelled').count(),
    }
    
    return Response(stats, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_appointments(request, doctor_id):
    """Get all appointments for a specific doctor"""
    if request.user.role not in ['doctor', 'admin']:
        return Response(
            {'error': 'Permission denied.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # If doctor is requesting, ensure they can only see their own appointments
    if request.user.role == 'doctor' and request.user.id != doctor_id:
        return Response(
            {'error': 'You can only view your own appointments.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    appointments = Appointment.objects.filter(
        doctor_id=doctor_id
    ).select_related('patient', 'doctor')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    serializer = AppointmentListSerializer(appointments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)