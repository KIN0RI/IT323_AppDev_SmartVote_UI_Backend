from django.contrib import admin
from .models import Candidate, Vote, ElectionSettings, VoterLog


@admin.register(ElectionSettings)
class ElectionSettingsAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date', 'end_date')


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display  = ('name', 'position', 'course', 'year_level', 'vote_count')
    list_filter   = ('position',)
    search_fields = ('name',)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display  = ('voter', 'candidate', 'position', 'timestamp')
    list_filter   = ('position',)
    search_fields = ('voter__full_name', 'candidate__name')


@admin.register(VoterLog)
class VoterLogAdmin(admin.ModelAdmin):
    list_display  = ('voter', 'login_time', 'ip_address')
    search_fields = ('voter__full_name', 'voter__student_id')
