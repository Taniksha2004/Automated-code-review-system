from rest_framework import serializers
from .models import CodeSubmission, ReviewResult, Issue, SupportedLanguage

class SupportedLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportedLanguage
        fields = ('id', 'name', 'extension', 'is_active')

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = (
            'id', 'rule_id', 'rule_name', 'severity', 'message',
            'line_number', 'column_number', 'suggestion'
        )

class ReviewResultSerializer(serializers.ModelSerializer):
    issues = IssueSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReviewResult
        fields = (
            'id', 'overall_score', 'total_issues', 'critical_issues',
            'error_issues', 'warning_issues', 'info_issues',
            'analysis_duration', 'created_at', 'issues'
        )

class CodeSubmissionSerializer(serializers.ModelSerializer):
    result = ReviewResultSerializer(read_only=True)
    language_name = serializers.CharField(source='language.name', read_only=True)
    
    class Meta:
        model = CodeSubmission
        fields = (
            'id', 'filename', 'language', 'language_name', 'code_content',
            'file_size', 'status', 'submitted_at', 'processed_at', 'result'
        )
        read_only_fields = ('id', 'file_size', 'status', 'submitted_at', 'processed_at')
    
    def validate_code_content(self):
        code_content = self.validated_data.get('code_content', '')
        if len(code_content.encode('utf-8')) > 1024 * 1024:  # 1MB limit
            raise serializers.ValidationError("File size exceeds 1MB limit")
        return code_content
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['file_size'] = len(validated_data['code_content'].encode('utf-8'))
        return super().create(validated_data)

class BulkSubmissionSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.DictField(),
        max_length=10  # Limit bulk uploads to 10 files
    )
    
    def validate_files(self, value):
        for file_data in value:
            if not all(key in file_data for key in ['filename', 'language', 'code_content']):
                raise serializers.ValidationError(
                    "Each file must have 'filename', 'language', and 'code_content'"
                )
        return value

class SubmissionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeSubmission
        fields = ('id', 'filename', 'status', 'submitted_at', 'processed_at')
