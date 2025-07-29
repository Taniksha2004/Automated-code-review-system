from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import CodeSubmission, SupportedLanguage, ReviewResult
from .serializers import (
    CodeSubmissionSerializer,
    SupportedLanguageSerializer,
    BulkSubmissionSerializer,
    SubmissionStatusSerializer
)
from .tasks import analyze_code_submission
import uuid

class SupportedLanguageListView(generics.ListAPIView):
    """List all supported programming languages"""
    queryset = SupportedLanguage.objects.filter(is_active=True)
    serializer_class = SupportedLanguageSerializer
    permission_classes = [permissions.IsAuthenticated]

class CodeSubmissionListCreateView(generics.ListCreateAPIView):
    """List user's submissions and create new submissions"""
    serializer_class = CodeSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = CodeSubmission.objects.filter(user=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by language
        language_filter = self.request.query_params.get('language')
        if language_filter:
            queryset = queryset.filter(language__name__icontains=language_filter)
        
        # Search by filename
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(filename__icontains=search)
        
        return queryset.order_by('-submitted_at')
    
    def perform_create(self, serializer):
        submission = serializer.save()
        # Queue analysis task
        analyze_code_submission.delay(str(submission.id))

class CodeSubmissionDetailView(generics.RetrieveAPIView):
    """Retrieve specific submission with results"""
    serializer_class = CodeSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CodeSubmission.objects.filter(user=self.request.user)

class SubmissionStatusView(generics.RetrieveAPIView):
    """Get submission status without full details"""
    serializer_class = SubmissionStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CodeSubmission.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_upload_view(request):
    """Handle bulk file uploads"""
    serializer = BulkSubmissionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    files_data = serializer.validated_data['files']
    created_submissions = []
    
    for file_data in files_data:
        # Get or create language
        try:
            language = SupportedLanguage.objects.get(
                name__iexact=file_data['language'],
                is_active=True
            )
        except SupportedLanguage.DoesNotExist:
            return Response(
                {'error': f"Unsupported language: {file_data['language']}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create submission
        submission = CodeSubmission.objects.create(
            user=request.user,
            filename=file_data['filename'],
            language=language,
            code_content=file_data['code_content'],
            file_size=len(file_data['code_content'].encode('utf-8'))
        )
        
        # Queue analysis
        analyze_code_submission.delay(str(submission.id))
        created_submissions.append(submission)
    
    # Serialize response
    serializer = CodeSubmissionSerializer(created_submissions, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check_view(request):
    """Health check endpoint"""
    from django.db import connection
    from django.core.cache import cache
    
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'services': {}
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['services']['database'] = 'healthy'
    except Exception as e:
        health_status['services']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Check cache
    try:
        cache.set('health_check', 'ok', 30)
        cache.get('health_check')
        health_status['services']['cache'] = 'healthy'
    except Exception as e:
        health_status['services']['cache'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Check Celery
    try:
        from celery import current_app
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        if stats:
            health_status['services']['celery'] = 'healthy'
        else:
            health_status['services']['celery'] = 'no workers'
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['services']['celery'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    status_code = status.HTTP_200_OK
    if health_status['status'] == 'unhealthy':
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif health_status['status'] == 'degraded':
        status_code = status.HTTP_200_OK
    
    return Response(health_status, status=status_code)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reanalyze_submission_view(request, pk):
    """Re-analyze a specific submission"""
    submission = get_object_or_404(
        CodeSubmission,
        id=pk,
        user=request.user
    )
    
    # Reset status
    submission.status = 'pending'
    submission.processed_at = None
    submission.save()
    
    # Delete existing results
    if hasattr(submission, 'result'):
        submission.result.delete()
    
    # Queue new analysis
    analyze_code_submission.delay(str(submission.id))
    
    return Response({
        'message': 'Reanalysis queued',
        'submission_id': str(submission.id)
    })
