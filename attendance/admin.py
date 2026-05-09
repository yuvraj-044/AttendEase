"""Admin configuration for AttendanceRequest model."""

from django.contrib import admin
from .models import AttendanceRequest


@admin.register(AttendanceRequest)
class AttendanceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'event', 'status', 'is_attended',
        'coordinator', 'teacher', 'created_at',
    ]
    list_filter = ['status', 'is_attended', 'created_at']
    search_fields = [
        'student__username', 'student__first_name',
        'event__name', 'reason',
    ]
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
