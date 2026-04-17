from rest_framework import serializers
from .models import Candidate, Vote, ElectionSettings, VoterLog
from django.contrib.auth import get_user_model

User = get_user_model()


class ElectionSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ElectionSettings
        fields = '__all__'


class CandidateSerializer(serializers.ModelSerializer):
    vote_count = serializers.ReadOnlyField()

    class Meta:
        model  = Candidate
        fields = ['id', 'name', 'position', 'course', 'year_level', 'bio', 'photo',
                  'vote_count', 'election', 'created_at']
        read_only_fields = ['created_at']


class VoteSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.name', read_only=True)
    position       = serializers.CharField(source='candidate.position', read_only=True)

    class Meta:
        model  = Vote
        fields = ['id', 'candidate', 'candidate_name', 'position', 'timestamp']
        read_only_fields = ['timestamp', 'candidate_name', 'position']

    def validate(self, data):
        voter     = self.context['request'].user
        candidate = data['candidate']

       
        if Vote.objects.filter(voter=voter, position=candidate.position).exists():
            raise serializers.ValidationError(
                f'You have already voted for {candidate.position}.'
            )
        return data

    def create(self, validated_data):
        voter = self.context['request'].user
        vote  = Vote.objects.create(
            voter=voter,
            candidate=validated_data['candidate'],
            position=validated_data['candidate'].position,
        )
        
        positions_count   = Candidate.objects.values('position').distinct().count()
        votes_cast        = Vote.objects.filter(voter=voter).count()
        if votes_cast >= positions_count:
            voter.has_voted = True
            voter.save(update_fields=['has_voted'])
        return vote


class VoterLogSerializer(serializers.ModelSerializer):
    name       = serializers.CharField(source='voter.full_name',  read_only=True)
    student_id = serializers.CharField(source='voter.student_id', read_only=True)
    email      = serializers.CharField(source='voter.email',      read_only=True)
    status     = serializers.SerializerMethodField()

    class Meta:
        model  = VoterLog
        fields = ['id', 'name', 'student_id', 'email', 'login_time', 'status', 'ip_address']

    def get_status(self, obj):
        return 'Voted' if obj.voter.has_voted else 'Pending'


class StudentVoterLogSerializer(serializers.ModelSerializer):
    """Serializer for the voter log — queries students directly so Pending
    students (who may never have triggered a VoterLog entry) are included,
    and admin accounts are excluded."""
    name       = serializers.CharField(source='full_name',  read_only=True)
    status     = serializers.SerializerMethodField()
    login_time = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'name', 'student_id', 'email', 'login_time', 'status']

    def get_status(self, obj):
        return 'Voted' if obj.has_voted else 'Pending'

    def get_login_time(self, obj):
        
        log = obj.logs.order_by('-login_time').first()
        return log.login_time.isoformat() if log else None


class DashboardStatsSerializer(serializers.Serializer):
    total_voters    = serializers.IntegerField()
    votes_cast      = serializers.IntegerField()
    remaining_voters = serializers.IntegerField()
    turnout_percent = serializers.FloatField()
    election_status = serializers.CharField()
    candidates_by_position = serializers.DictField()