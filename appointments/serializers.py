from rest_framework import serializers
from django.utils import timezone
from core.models import User
from .models import Appointment

class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('doctor', 'appointment_date', 'reason')
    
    def validate_doctor(self, value):
        if value.role != 'doctor':
            raise serializers.ValidationError("Selected user is not a doctor.")
        return value
    
    def validate_appointment_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Appointment date must be in the future.")
        return value
    
    def create(self, validated_data):
        # Set patient from request user
        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)

class AppointmentListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    patient_email = serializers.CharField(source='patient.email', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_email = serializers.CharField(source='doctor.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = (
            'id', 'patient', 'patient_name', 'patient_email',
            'doctor', 'doctor_name', 'doctor_email',
            'appointment_date', 'status', 'status_display',
            'reason', 'notes', 'created_at', 'updated_at'
        )

class AppointmentDetailSerializer(serializers.ModelSerializer):
    patient_details = serializers.SerializerMethodField()
    doctor_details = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = (
            'id', 'patient_details', 'doctor_details',
            'appointment_date', 'status', 'status_display',
            'reason', 'notes', 'created_at', 'updated_at'
        )
    
    def get_patient_details(self, obj):
        return {
            'id': obj.patient.id,
            'name': obj.patient.name,
            'email': obj.patient.email
        }
    
    def get_doctor_details(self, obj):
        return {
            'id': obj.doctor.id,
            'name': obj.doctor.name,
            'email': obj.doctor.email
        }

class AppointmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('status', 'notes', 'appointment_date')
    
    def validate_status(self, value):
        current_status = self.instance.status if self.instance else None
        user = self.context['request'].user
        
        # Only doctors can confirm appointments
        if value == 'confirmed' and user.role != 'doctor':
            raise serializers.ValidationError("Only doctors can confirm appointments.")
        
        # Only allow certain status transitions
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': []
        }
        
        if current_status and value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(f"Cannot change status from {current_status} to {value}.")
        
        return value
    
    def validate_appointment_date(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Appointment date must be in the future.")
        return value