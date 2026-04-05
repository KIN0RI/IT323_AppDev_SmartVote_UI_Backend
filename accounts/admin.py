from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Voter

@admin.register(Voter)
class VoterAdmin(BaseUserAdmin):
    list_display  = ('student_id', 'full_name', 'email', 'role', 'has_voted', 'face_verified')
    list_filter   = ('role', 'has_voted', 'face_verified')
    search_fields = ('student_id', 'full_name', 'email')
    ordering      = ('full_name',)
    fieldsets = (
        (None,           {'fields': ('student_id', 'password')}),
        ('Personal',     {'fields': ('full_name', 'email', 'course', 'year_level')}),
        ('Status',       {'fields': ('role', 'has_voted', 'face_verified')}),
        ('Permissions',  {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('student_id', 'email', 'full_name', 'course', 'year_level',
                        'role', 'password1', 'password2'),
        }),
    )
