from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class VoterManager(BaseUserManager):
    def create_user(self, student_id, email, full_name, password=None, **extra):
        if not student_id:
            raise ValueError('Student ID is required')
        email = self.normalize_email(email)
        user = self.model(student_id=student_id, email=email, full_name=full_name, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_id, email, full_name, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('role', 'admin')
        return self.create_user(student_id, email, full_name, password, **extra)


class Voter(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [('student', 'Student'), ('admin', 'Admin')]

    student_id  = models.CharField(max_length=20, unique=True, verbose_name='Username') 
    email       = models.EmailField(unique=True)
    full_name   = models.CharField(max_length=150)
    course      = models.CharField(max_length=100, blank=True, default='')
    year_level  = models.CharField(max_length=20, blank=True, default='')
    role        = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    has_voted   = models.BooleanField(default=False)
    face_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)

    objects = VoterManager()

    USERNAME_FIELD  = 'student_id'
    REQUIRED_FIELDS = ['email', 'full_name']

    class Meta:
        verbose_name = 'Voter'
        ordering = ['full_name']

    def __str__(self):
        return f'{self.full_name} ({self.student_id})'