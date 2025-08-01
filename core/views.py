from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from .models import User, DoctorStatus
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    DoctorSerializer,
    PatientSerializer,
    DoctorStatusSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.validated_data['user']
    login(request, user)
    
    # Generate tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class DoctorListView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(role='doctor').order_by('name')

class PatientListView(generics.ListAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only doctors can view patient list
        if self.request.user.role == 'doctor':
            return User.objects.filter(role='patient').order_by('name')
        return User.objects.none()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_doctor_status(request):
    if request.user.role != 'doctor':
        return Response(
            {'error': 'Only doctors can update their status'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        doctor_status, created = DoctorStatus.objects.get_or_create(
            doctor=request.user
        )
        
        is_online = request.data.get('is_online')
        if is_online is not None:
            doctor_status.is_online = is_online
            doctor_status.save()
            
            return Response({
                'message': f'Status updated to {"online" if is_online else "offline"}',
                'status': {
                    'is_online': doctor_status.is_online,
                    'last_seen': doctor_status.last_seen
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'is_online field is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_doctor_status(request, doctor_id):
    try:
        doctor = User.objects.get(id=doctor_id, role='doctor')
        doctor_status, created = DoctorStatus.objects.get_or_create(
            doctor=doctor
        )
        
        serializer = DoctorStatusSerializer(doctor_status)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Doctor not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_doctor_statuses(request):
    doctor_statuses = DoctorStatus.objects.select_related('doctor').all()
    serializer = DoctorStatusSerializer(doctor_statuses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)