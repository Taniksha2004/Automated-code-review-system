#!/usr/bin/env python
"""
Database setup script for Automated Code Review System
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'code_review_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
from reviews.models import SupportedLanguage

User = get_user_model()

def setup_database():
    """Setup database with initial data"""
    print("🚀 Setting up Automated Code Review System Database...")
    
    # Run migrations
    print("📦 Running database migrations...")
    call_command('migrate', verbosity=1)
    
    # Create superuser if it doesn't exist
    print("👤 Creating admin user...")
    if not User.objects.filter(email='admin@codereview.com').exists():
        User.objects.create_superuser(
            email='admin@codereview.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print("✅ Admin user created: admin@codereview.com / admin123")
    else:
        print("ℹ️  Admin user already exists")
    
    # Create test user
    print("👥 Creating test user...")
    if not User.objects.filter(email='developer@example.com').exists():
        User.objects.create_user(
            email='developer@example.com',
            password='dev123',
            first_name='Test',
            last_name='Developer'
        )
        print("✅ Test user created: developer@example.com / dev123")
    else:
        print("ℹ️  Test user already exists")
    
    # Setup supported languages
    print("🔧 Setting up supported languages...")
    languages = [
        {
            'name': 'Python',
            'extension': 'py',
            'analyzer_class': 'reviews.analyzers.PythonAnalyzer',
            'is_active': True
        },
        {
            'name': 'JavaScript',
            'extension': 'js',
            'analyzer_class': 'reviews.analyzers.JavaScriptAnalyzer',
            'is_active': True
        },
        {
            'name': 'TypeScript',
            'extension': 'ts',
            'analyzer_class': 'reviews.analyzers.JavaScriptAnalyzer',
            'is_active': True
        },
        {
            'name': 'Java',
            'extension': 'java',
            'analyzer_class': 'reviews.analyzers.JavaAnalyzer',
            'is_active': False
        }
    ]
    
    for lang_data in languages:
        language, created = SupportedLanguage.objects.get_or_create(
            name=lang_data['name'],
            defaults=lang_data
        )
        if created:
            print(f"✅ Added language: {lang_data['name']}")
        else:
            print(f"ℹ️  Language already exists: {lang_data['name']}")
    
    print("\n🎉 Database setup completed successfully!")
    print("\n📋 Summary:")
    print("- Admin user: admin@codereview.com / admin123")
    print("- Test user: developer@example.com / dev123")
    print("- Supported languages: Python, JavaScript, TypeScript")
    print("- API Documentation: http://localhost:8000/api/docs/")
    print("- Admin Panel: http://localhost:8000/admin/")

if __name__ == '__main__':
    setup_database()
