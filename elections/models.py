from django.db import models
from django.conf import settings


class ElectionSettings(models.Model):
    STATUS_CHOICES = [('open', 'Open'), ('closed', 'Closed'), ('upcoming', 'Upcoming')]

    title                     = models.CharField(max_length=200, default='USTP Student Council Election')
    start_date                = models.DateTimeField()
    end_date                  = models.DateTimeField()
    status                    = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    allow_multiple_votes      = models.BooleanField(default=False)
    require_face_verification = models.BooleanField(default=True)
    created_at                = models.DateTimeField(auto_now_add=True)
    updated_at                = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Election Settings'

    def __str__(self):
        return self.title


class Candidate(models.Model):
    POSITION_CHOICES = [
        ('President',      'President'),
        ('Vice President', 'Vice President'),
        ('Secretary',      'Secretary'),
        ('Treasurer',      'Treasurer'),
        ('Auditor',        'Auditor'),
    ]

    name       = models.CharField(max_length=150)
    position   = models.CharField(max_length=30, choices=POSITION_CHOICES)
    course     = models.CharField(max_length=100, blank=True, default='')
    year_level = models.CharField(max_length=20, blank=True, default='')
    bio        = models.TextField(blank=True, default='')
    photo      = models.ImageField(upload_to='candidates/', blank=True, null=True)
    election   = models.ForeignKey(
        ElectionSettings, on_delete=models.CASCADE,
        related_name='candidates', null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position', 'name']

    def __str__(self):
        return f'{self.name} — {self.position}'

    @property
    def vote_count(self):
        return self.votes.count()


class Vote(models.Model):
    voter     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes'
    )
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    position  = models.CharField(max_length=30)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'position')
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.voter.full_name} → {self.candidate.name} ({self.position})'


class VoterLog(models.Model):
    voter      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='logs'
    )
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ['-login_time']

    def __str__(self):
        return f'{self.voter.full_name} logged in at {self.login_time}'