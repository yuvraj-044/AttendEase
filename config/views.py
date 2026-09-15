"""
Project-level views.

These views don't belong to any specific app — they serve
project-wide pages that live in the top-level templates/ directory.
"""

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def about(request):
    """About AttendEase page — project info, tech stack, and team."""
    features = [
        ('bi-shield-lock-fill',       'Role-Based Access',     'Separate dashboards for Students, Coordinators, and Teachers.'),
        ('bi-calendar-event-fill',    'Event Management',      'Coordinators create and manage college events with full CRUD.'),
        ('bi-check2-circle',          'Two-Stage Approval',    'Requests go from Coordinator to Teacher before final sign-off.'),
        ('bi-file-earmark-excel-fill','Excel Export',          'Teachers can download division attendance records any time.'),
        ('bi-people-fill',            'Division System',       'Students and teachers are grouped by class division.'),
        ('bi-send-fill',              'Open Event Support',    'External events skip coordinator and go directly to the teacher.'),
    ]
    stack = [
        ('bi-filetype-py',      'Python 3'),
        ('bi-box',              'Django 4.2'),
        ('bi-database-fill',    'SQLite'),
        ('bi-bootstrap-fill',   'Bootstrap 5'),
        ('bi-filetype-js',      'JavaScript'),
        ('bi-file-earmark-code','openpyxl'),
    ]
    team = [
        ('YB', 'Yuvraj Baglane',   'Full Stack Developer'),
        ('BC', 'Bhushan Chandak',  'Frontend & UI/UX'),
        ('RG', 'Rakshit Gogulwar', 'Core Logic & Testing'),
    ]
    return render(request, 'about.html', {
        'current_year': datetime.now().year,
        'features': features,
        'stack': stack,
        'team': team,
    })
