from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegisterSerializer, VoterProfileSerializer, SmartVoteTokenSerializer


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/  →  { access, refresh, role, full_name, student_id }"""
    serializer_class = SmartVoteTokenSerializer


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
