from django.urls import path
from . import views

urlpatterns = [
    # Languages
    path('languages/', views.SupportedLanguageListView.as_view(), name='supported_languages'),
    
    # Submissions
    path('submissions/', views.CodeSubmissionListCreateView.as_view(), name='submissions'),
    path('submissions/<uuid:pk>/', views.CodeSubmissionDetailView.as_view(), name='submission_detail'),
    path('submissions/<uuid:pk>/status/', views.SubmissionStatusView.as_view(), name='submission_status'),
    path('submissions/<uuid:pk>/reanalyze/', views.reanalyze_submission_view, name='reanalyze_submission'),
    
    # Bulk operations
    path('bulk-upload/', views.bulk_upload_view, name='bulk_upload'),
    
    # Health check
    path('health/', views.health_check_view, name='health_check'),
]
