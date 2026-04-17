from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import Candidate, Vote, ElectionSettings
from .serializers import (
    CandidateSerializer, VoteSerializer, ElectionSettingsSerializer,
    VoterLogSerializer
)

User = get_user_model()



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def candidates(request):
    """
    GET  /api/candidates/  — list all candidates
    POST /api/candidates/  — add a candidate (admin only)
    """
    if request.method == 'GET':
        qs       = Candidate.objects.all()
        position = request.query_params.get('position')
        if position:
            qs = qs.filter(position=position)
        serializer = CandidateSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    if request.user.role != 'admin' and not request.user.is_staff:
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = CandidateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def candidate_detail(request, pk):
    """GET/PUT/DELETE /api/candidates/<pk>/"""
    try:
        candidate = Candidate.objects.get(pk=pk)
    except Candidate.DoesNotExist:
        return Response({'error': 'Candidate not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(CandidateSerializer(candidate, context={'request': request}).data)

    if request.user.role != 'admin' and not request.user.is_staff:
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'PUT':
        serializer = CandidateSerializer(candidate, data=request.data, partial=True,
                                         context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    candidate.delete()
    return Response({'message': 'Candidate deleted.'}, status=status.HTTP_204_NO_CONTENT)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cast_vote(request):
    """POST /api/vote/"""
    if request.user.role == 'admin':
        return Response({'error': 'Admins cannot vote.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = VoteSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        vote = serializer.save()
        return Response(
            {'message': f'Vote cast for {vote.candidate.name} ({vote.position}).'},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_votes(request):
    """GET /api/vote/my/"""
    votes      = Vote.objects.filter(voter=request.user).select_related('candidate')
    serializer = VoteSerializer(votes, many=True, context={'request': request})
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([AllowAny])
def results(request):
    """GET /api/results/"""
    from django.db.models import Count
    positions = Candidate.objects.values_list('position', flat=True).distinct()
    data = {}
    for pos in positions:
        qs = Candidate.objects.filter(position=pos).annotate(
            total_votes=Count('votes')
        ).order_by('-total_votes')
        data[pos] = CandidateSerializer(qs, many=True, context={'request': request}).data
    return Response(data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """GET /api/dashboard/"""
    if request.user.role != 'admin' and not request.user.is_staff:
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    total_voters = User.objects.filter(role='student').count()
    votes_cast   = User.objects.filter(role='student', has_voted=True).count()
    remaining    = total_voters - votes_cast
    turnout      = round((votes_cast / total_voters * 100), 2) if total_voters else 0.0

    try:
        election  = ElectionSettings.objects.latest('created_at')
        el_status = election.status
    except ElectionSettings.DoesNotExist:
        el_status = 'N/A'

    from django.db.models import Count
    positions = Candidate.objects.values_list('position', flat=True).distinct()
    by_pos    = {}
    for pos in positions:
        qs = Candidate.objects.filter(position=pos).annotate(
            total_votes=Count('votes')
        ).order_by('-total_votes')
        by_pos[pos] = CandidateSerializer(qs, many=True, context={'request': request}).data

    return Response({
        'total_voters':           total_voters,
        'votes_cast':             votes_cast,
        'remaining_voters':       remaining,
        'turnout_percent':        turnout,
        'election_status':        el_status,
        'candidates_by_position': by_pos,
    })




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def voter_log(request):
    """GET /api/voter-log/"""
    if request.user.role != 'admin' and not request.user.is_staff:
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    
    students      = User.objects.filter(role='student')
    search        = request.query_params.get('search', '')
    status_filter = request.query_params.get('status', 'All')

    if search:
        students = students.filter(full_name__icontains=search) | \
                   students.filter(student_id__icontains=search)
    if status_filter == 'Voted':
        students = students.filter(has_voted=True)
    elif status_filter == 'Pending':
        students = students.filter(has_voted=False)

    from .serializers import StudentVoterLogSerializer
    serializer = StudentVoterLogSerializer(students, many=True)
    return Response(serializer.data)



@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
def election_settings(request):
    """GET/POST/PUT /api/election-settings/"""
    if request.user.role != 'admin' and not request.user.is_staff:
        return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        try:
            obj = ElectionSettings.objects.latest('created_at')
            return Response(ElectionSettingsSerializer(obj).data)
        except ElectionSettings.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        serializer = ElectionSettingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        obj = ElectionSettings.objects.latest('created_at')
    except ElectionSettings.DoesNotExist:
        return Response({'error': 'No settings found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ElectionSettingsSerializer(obj, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cast_vote(request):
    """POST /api/vote/"""
    if request.user.role == 'admin':
        return Response({'error': 'Admins cannot vote.'}, status=status.HTTP_403_FORBIDDEN)

    
    try:
        election = ElectionSettings.objects.latest('created_at')
        if election.status != 'open':
            return Response(
                {'detail': 'Election is currently closed.'},
                status=status.HTTP_403_FORBIDDEN
            )
    except ElectionSettings.DoesNotExist:
        pass

    serializer = VoteSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        vote = serializer.save()
        return Response(
            {'message': f'Vote cast for {vote.candidate.name} ({vote.position}).'},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)