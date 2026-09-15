"""Attendance app URL configuration."""

from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # ── Student ──────────────────────────────────────────────
    path('student/',                          views.student_dashboard,    name='student_dashboard'),
    path('student/submit/',                   views.submit_request,       name='submit_request'),
    path('student/request/<int:pk>/',         views.request_detail,       name='request_detail_student'),

    # ── Coordinator ───────────────────────────────────────────
    path('coordinator/',                      views.coordinator_dashboard, name='coordinator_dashboard'),
    path('coordinator/review/<int:pk>/',      views.coordinator_review,    name='coordinator_review'),

    # ── Teacher ───────────────────────────────────────────────
    path('teacher/',                          views.teacher_dashboard,     name='teacher_dashboard'),
    path('teacher/export/excel/',             views.teacher_export_excel,  name='teacher_export_excel'),
    path('teacher/review/<int:pk>/',          views.teacher_review,        name='teacher_review'),
    path('teacher/mark-attendance/<int:pk>/', views.mark_attendance,       name='mark_attendance'),
]
