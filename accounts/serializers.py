from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = User
        fields = ['student_id', 'email', 'full_name', 'course', 'year_level', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class VoterProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'student_id', 'email', 'full_name', 'course',
                  'year_level', 'role', 'has_voted', 'face_verified', 'date_joined']
        read_only_fields = ['student_id', 'role', 'has_voted', 'face_verified', 'date_joined']


class SmartVoteTokenSerializer(TokenObtainPairSerializer):
    """Extend JWT payload with role so the frontend knows where to redirect."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role']       = user.role
        token['full_name']  = user.full_name
        token['student_id'] = user.student_id
        return token
    