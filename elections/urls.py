from django.urls import path
from . import views

urlpatterns = [
    path('candidates/',           views.candidates,       name='candidates'),
    path('candidates/<int:pk>/',  views.candidate_detail, name='candidate-detail'),

    path('vote/',                 views.cast_vote,        name='cast-vote'),
    path('vote/my/',              views.my_votes,         name='my-votes'),

    path('results/',              views.results,          name='results'),

    path('dashboard/',            views.dashboard_stats,  name='dashboard'),
    path('voter-log/',            views.voter_log,        name='voter-log'),
    path('election-settings/',    views.election_settings,name='election-settings'),
]
