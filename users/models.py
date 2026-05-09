"""
Custom User model with role-based access control.
Roles: Student, Event Coordinator, Class Teacher
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Extended user model that adds role, student ID, department, and phone.
    The role field determines which dashboard and permissions the user gets.
    """

    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        COORDINATOR = 'coordinator', 'Event Coordinator'
        TEACHER = 'teacher', 'Class Teacher'

    class Division(models.TextChoices):
        A = 'A', 'Division A'
        B = 'B', 'Division B'
        C = 'C', 'Division C'
        D = 'D', 'Division D'
        E = 'E', 'Division E'
        F = 'F', 'Division F'
        G = 'G', 'Division G'
        H = 'H', 'Division H'
        I = 'I', 'Division I'
        J = 'J', 'Division J'
        K = 'K', 'Division K'
        L = 'L', 'Division L'
        M = 'M', 'Division M'
        N = 'N', 'Division N'
        O = 'O', 'Division O'
        P = 'P', 'Division P'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text='Determines the user\'s access level and dashboard.'
    )
    division = models.CharField(
        max_length=5,
        choices=Division.choices,
        blank=True,
        help_text='Class division (required for students and teachers).'
    )
    student_id = models.CharField(
        max_length=20,
        blank=True,
        help_text='Student roll number or ID (students only).'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text='Department or branch name.'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        help_text='Contact phone number.'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_coordinator(self):
        return self.role == self.Role.COORDINATOR

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER
