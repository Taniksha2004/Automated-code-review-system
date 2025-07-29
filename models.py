from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class SupportedLanguage(models.Model):
    """Supported programming languages for analysis"""
    name = models.CharField(max_length=50, unique=True)
    extension = models.CharField(max_length=10)
    analyzer_class = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'supported_languages'
    
    def __str__(self):
        return self.name

class CodeSubmission(models.Model):
    """Code submissions for analysis"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    filename = models.CharField(max_length=255)
    language = models.ForeignKey(SupportedLanguage, on_delete=models.CASCADE)
    code_content = models.TextField()
    file_size = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'code_submissions'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['submitted_at']),
            models.Index(fields=['language']),
        ]
    
    def __str__(self):
        return f"{self.filename} - {self.user.email}"

class ReviewResult(models.Model):
    """Analysis results for code submissions"""
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField(CodeSubmission, on_delete=models.CASCADE, related_name='result')
    overall_score = models.FloatField(default=0.0)
    total_issues = models.IntegerField(default=0)
    critical_issues = models.IntegerField(default=0)
    error_issues = models.IntegerField(default=0)
    warning_issues = models.IntegerField(default=0)
    info_issues = models.IntegerField(default=0)
    analysis_duration = models.FloatField(default=0.0)  # in seconds
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_results'
        indexes = [
            models.Index(fields=['submission']),
            models.Index(fields=['overall_score']),
        ]
    
    def __str__(self):
        return f"Result for {self.submission.filename}"

class Issue(models.Model):
    """Individual issues found in code analysis"""
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    result = models.ForeignKey(ReviewResult, on_delete=models.CASCADE, related_name='issues')
    rule_id = models.CharField(max_length=100)
    rule_name = models.CharField(max_length=200)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    message = models.TextField()
    line_number = models.IntegerField()
    column_number = models.IntegerField(default=0)
    suggestion = models.TextField(blank=True)
    
    class Meta:
        db_table = 'issues'
        indexes = [
            models.Index(fields=['result', 'severity']),
            models.Index(fields=['rule_id']),
        ]
    
    def __str__(self):
        return f"{self.rule_name} - Line {self.line_number}"

class UserStats(models.Model):
    """Aggregated statistics for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stats')
    total_submissions = models.IntegerField(default=0)
    total_issues_found = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    last_submission = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_stats'
    
    def __str__(self):
        return f"Stats for {self.user.email}"
