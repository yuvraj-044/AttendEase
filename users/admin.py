"""Admin configuration for CustomUser model."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Extend default UserAdmin to show custom fields."""

    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'division', 'grade', 'department', 'is_active']
    list_filter = ['role', 'division', 'grade', 'department', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'student_id']

    # Add custom fields to the admin edit form
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('role', 'division', 'grade', 'student_id', 'department', 'phone'),
        }),
    )

    # Add custom fields to the admin create form
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile', {
            'fields': ('role', 'division', 'grade', 'student_id', 'department', 'phone'),
        }),
    )
