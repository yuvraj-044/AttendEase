"""
Event model — represents college events that students can request to attend.
"""

from django.conf import settings
from django.db import models


class Event(models.Model):
    """
    Represents a college event (seminar, workshop, competition, etc.).
    Created by coordinators; students select from active events when submitting requests.
    """

    name = models.CharField(max_length=200, help_text='Name of the event.')
    description = models.TextField(help_text='Detailed description of the event.')
    date = models.DateField(help_text='Date of the event.')
    time = models.TimeField(help_text='Start time of the event.')
    venue = models.CharField(max_length=200, help_text='Event venue/location.')
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events',
        help_text='The coordinator who created this event.'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Only active events are shown to students.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return f"{self.name} — {self.date.strftime('%b %d, %Y')}"
