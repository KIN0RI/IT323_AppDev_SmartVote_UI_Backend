from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, VoterProfileSerializer, SmartVoteTokenSerializer


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/  →  { access, refresh, role, full_name, student_id }"""
    serializer_class = SmartVoteTokenSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_with_email(request):
    """POST /api/auth/login-email/  — login using email + password"""
    from django.contrib.auth import authenticate

    email    = request.data.get('email', '').strip()
    password = request.data.get('password', '')

    try:
        user = get_user_model().objects.get(email=email)
    except get_user_model().DoesNotExist:
        return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(request, username=user.student_id, password=password)
    if user is None:
        return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    refresh['role']       = user.role
    refresh['full_name']  = user.full_name
    refresh['student_id'] = user.student_id

    return Response({
        'access':     str(refresh.access_token),
        'refresh':    str(refresh),
        'role':       user.role,
        'full_name':  user.full_name,
        'student_id': user.student_id,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """POST /api/auth/register/"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Registration successful. You can now log in.'},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    """GET/PUT /api/auth/profile/"""
    if request.method == 'GET':
        serializer = VoterProfileSerializer(request.user)
        return Response(serializer.data)

    serializer = VoterProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)