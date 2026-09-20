"""
AttendanceRequest model — tracks the multi-step approval workflow.

Workflow:
  Student submits → status=pending
  Coordinator approves → status=coordinator_approved
  Teacher approves → status=teacher_approved
  Teacher can reject at final stage → status=teacher_rejected
"""

from django.conf import settings
from django.db import models
from django.utils import timezone


class AttendanceRequest(models.Model):
    """
    Represents a student's request to attend an event.
    Goes through a two-stage approval process (Coordinator → Teacher),
    or directly to Teacher for Open Events.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COORDINATOR_APPROVED = 'coordinator_approved', 'Coordinator Approved'
        COORDINATOR_REJECTED = 'coordinator_rejected', 'Coordinator Rejected'
        TEACHER_APPROVED = 'teacher_approved', 'Teacher Approved'
        TEACHER_REJECTED = 'teacher_rejected', 'Teacher Rejected'

    class EventType(models.TextChoices):
        COORDINATOR = 'coordinator', 'Coordinator Event'
        OPEN = 'open', 'Open Event'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_requests',
        help_text='The student who submitted this request.'
    )
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_requests',
        help_text='The internal college event the student wants to attend.'
    )
    event_type = models.CharField(
        max_length=15,
        choices=EventType.choices,
        default=EventType.COORDINATOR,
        db_index=True,
        help_text='Coordinator Event follows full flow; Open Event skips coordinator and goes directly to teacher.'
    )
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text='Current status in the approval workflow.'
    )
    reason = models.TextField(
        help_text='Why the student wants to attend this event.'
    )
    external_event_name = models.CharField(
        max_length=200,
        blank=True,
        help_text='Name of the external/open event.'
    )
    external_college_name = models.CharField(
        max_length=200,
        blank=True,
        help_text='College or institute hosting the external/open event.'
    )
    external_event_location = models.CharField(
        max_length=200,
        blank=True,
        help_text='Location or venue of the external/open event.'
    )
    external_event_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date of the external/open event.'
    )
    external_event_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Time of the external/open event.'
    )

    # Coordinator review
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinator_reviews',
        help_text='Coordinator who reviewed this request.'
    )
    coordinator_remarks = models.TextField(
        blank=True,
        help_text='Coordinator\'s remarks on this request.'
    )
    coordinator_action_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the coordinator took action.'
    )

    # Teacher review
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teacher_reviews',
        help_text='Teacher who reviewed this request.'
    )
    teacher_remarks = models.TextField(
        blank=True,
        help_text='Teacher\'s remarks on this request.'
    )
    teacher_action_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the teacher took action.'
    )

    # Final attendance
    is_attended = models.BooleanField(
        default=False,
        help_text='Whether the student actually attended the event.'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Attendance Request'
        verbose_name_plural = 'Attendance Requests'
        # Prevent duplicate requests from same student for same event
        unique_together = ['student', 'event']

    def __str__(self):
        return f"{self.student.get_full_name() or self.student.username} → {self.display_event_name} [{self.get_status_display()}]"

    @property
    def display_event_name(self):
        if self.event_type == self.EventType.OPEN:
            return self.external_event_name or 'Open Event'
        return self.event.name if self.event else 'Event unavailable'

    @property
    def display_event_venue(self):
        if self.event_type == self.EventType.OPEN:
            if self.external_college_name and self.external_event_location:
                return f'{self.external_college_name}, {self.external_event_location}'
            return self.external_college_name or self.external_event_location or '—'
        return self.event.venue if self.event else '—'

    @property
    def display_event_date(self):
        if self.event_type == self.EventType.OPEN:
            return self.external_event_date
        return self.event.date if self.event else None

    @property
    def display_event_time(self):
        if self.event_type == self.EventType.OPEN:
            return self.external_event_time
        return self.event.time if self.event else None

    @property
    def export_event_date(self):
        return self.display_event_date or timezone.localdate(self.created_at)

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    @property
    def is_approved(self):
        return self.status == self.Status.TEACHER_APPROVED

    @property
    def is_rejected(self):
        return self.status in [
            self.Status.COORDINATOR_REJECTED,
            self.Status.TEACHER_REJECTED,
        ]
