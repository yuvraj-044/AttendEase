"""
attendance.views
~~~~~~~~~~~~~~~~
Re-exports all view callables so that urls.py can import from
``attendance.views`` without caring about the internal file layout.

Layout
------
student.py     — student dashboard, submit request, request detail
coordinator.py — coordinator dashboard, coordinator review
teacher.py     — teacher dashboard, teacher review, mark attendance
exports.py     — Excel export for teachers
"""

from .student import (
    student_dashboard,
    submit_request,
    request_detail,
)
from .coordinator import (
    coordinator_dashboard,
    coordinator_review,
)
from .teacher import (
    teacher_dashboard,
    teacher_review,
    mark_attendance,
)
from .exports import teacher_export_excel

__all__ = [
    # Student
    'student_dashboard',
    'submit_request',
    'request_detail',
    # Coordinator
    'coordinator_dashboard',
    'coordinator_review',
    # Teacher
    'teacher_dashboard',
    'teacher_review',
    'mark_attendance',
    # Exports
    'teacher_export_excel',
]
