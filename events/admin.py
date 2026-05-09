"""Admin configuration for Event model."""

from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'time', 'venue', 'organizer', 'is_active', 'created_at']
    list_filter = ['is_active', 'date']
    search_fields = ['name', 'venue', 'description']
    date_hierarchy = 'date'
