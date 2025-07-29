from celery import shared_task
from django.utils import timezone
from .models import CodeSubmission, ReviewResult, Issue
from .analyzers import get_analyzer
import time
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def analyze_code_submission(self, submission_id):
    """Celery task to analyze code submission"""
    try:
        submission = CodeSubmission.objects.get(id=submission_id)
        submission.status = 'processing'
        submission.save()
        
        logger.info(f"Starting analysis for submission {submission_id}")
        start_time = time.time()
        
        # Get analyzer for the language
        analyzer = get_analyzer(submission.language.name.lower())
        
        # Perform analysis
        analysis_result = analyzer.analyze(
            submission.code_content,
            submission.filename
        )
        
        end_time = time.time()
        analysis_duration = end_time - start_time
        
        # Create review result
        review_result = ReviewResult.objects.create(
            submission=submission,
            overall_score=analysis_result['overall_score'],
            total_issues=analysis_result['total_issues'],
            critical_issues=analysis_result['critical_issues'],
            error_issues=analysis_result['error_issues'],
            warning_issues=analysis_result['warning_issues'],
            info_issues=analysis_result['info_issues'],
            analysis_duration=analysis_duration
        )
        
        # Create individual issues
        for issue_data in analysis_result['issues']:
            Issue.objects.create(
                result=review_result,
                **issue_data
            )
        
        # Update submission status
        submission.status = 'completed'
        submission.processed_at = timezone.now()
        submission.save()
        
        # Update user stats
        update_user_stats.delay(submission.user.id)
        
        logger.info(f"Analysis completed for submission {submission_id}")
        
        return {
            'submission_id': str(submission_id),
            'status': 'completed',
            'score': analysis_result['overall_score'],
            'issues_count': analysis_result['total_issues']
        }
        
    except CodeSubmission.DoesNotExist:
        logger.error(f"Submission {submission_id} not found")
        return {'error': 'Submission not found'}
    
    except Exception as exc:
        logger.error(f"Analysis failed for submission {submission_id}: {str(exc)}")
        
        # Update submission status to failed
        try:
            submission = CodeSubmission.objects.get(id=submission_id)
            submission.status = 'failed'
            submission.processed_at = timezone.now()
            submission.save()
        except CodeSubmission.DoesNotExist:
            pass
        
        # Retry the task
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        return {'error': str(exc)}

@shared_task
def update_user_stats(user_id):
    """Update user statistics after analysis completion"""
    from django.contrib.auth import get_user_model
    from .models import UserStats
    from django.db.models import Avg, Count, Max
    
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        
        # Calculate stats
        submissions = CodeSubmission.objects.filter(
            user=user,
            status='completed'
        )
        
        stats_data = submissions.aggregate(
            total_submissions=Count('id'),
            average_score=Avg('result__overall_score'),
            total_issues=Count('result__issues'),
            last_submission=Max('submitted_at')
        )
        
        # Update or create user stats
        user_stats, created = UserStats.objects.get_or_create(
            user=user,
            defaults=stats_data
        )
        
        if not created:
            for key, value in stats_data.items():
                setattr(user_stats, key, value or 0)
            user_stats.save()
        
        logger.info(f"Updated stats for user {user_id}")
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
    except Exception as exc:
        logger.error(f"Failed to update stats for user {user_id}: {str(exc)}")

@shared_task
def cleanup_old_submissions():
    """Clean up old submissions and results"""
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    
    # Delete old submissions
    old_submissions = CodeSubmission.objects.filter(
        submitted_at__lt=cutoff_date,
        status__in=['completed', 'failed']
    )
    
    count = old_submissions.count()
    old_submissions.delete()
    
    logger.info(f"Cleaned up {count} old submissions")
    
    return {'cleaned_submissions': count}
