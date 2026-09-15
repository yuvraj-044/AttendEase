"""
Export views — data download helpers for teachers.

  teacher_export_excel — download all division attendance records as .xlsx
"""

from datetime import time

from django.http import HttpResponse

from users.decorators import role_required
from ..models import AttendanceRequest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_month(value):
    """Return (None, int) month number from a query-string value, or (None, None)."""
    if not value:
        return None, None
    try:
        month = int(value)
        if 1 <= month <= 12:
            return None, month
    except (TypeError, ValueError):
        pass
    return None, None


def _division_requests(user, month_value=''):
    """
    Return all attendance requests for a teacher's division,
    sorted chronologically by event date then student ID.
    Optionally filtered to a single calendar month.
    """
    qs = AttendanceRequest.objects.filter(
        student__division=user.division
    ).select_related('student', 'event')

    _, month = _parse_month(month_value)
    if month:
        qs = qs.filter(created_at__month=month)

    return sorted(
        qs,
        key=lambda r: (
            r.export_event_date,
            r.display_event_time or time.min,
            r.student.student_id or '',
            r.student.get_full_name() or r.student.username,
        ),
    )


def _export_status(att_request):
    """Map an AttendanceRequest to a human-readable export status string."""
    if att_request.status == AttendanceRequest.Status.TEACHER_APPROVED:
        return 'Approved'
    if att_request.status in [
        AttendanceRequest.Status.COORDINATOR_REJECTED,
        AttendanceRequest.Status.TEACHER_REJECTED,
    ]:
        return 'Rejected'
    return 'Pending'


# ── View ──────────────────────────────────────────────────────────────────────

@role_required('teacher')
def teacher_export_excel(request):
    """Download division attendance records as an Excel workbook (.xlsx)."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Attendance'

    headers = ['Student Name', 'Roll No', 'Division', 'Event Name', 'Event Type', 'Date', 'Status']
    sheet.append(headers)

    header_fill = PatternFill(start_color='D9EAF7', end_color='D9EAF7', fill_type='solid')
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill

    month_value = request.GET.get('month', '')
    for record in _division_requests(request.user, month_value):
        sheet.append([
            record.student.get_full_name() or record.student.username,
            record.student.student_id or '',
            record.student.get_division_display() or record.student.division or '',
            record.display_event_name,
            record.get_event_type_display(),
            record.export_event_date.strftime('%Y-%m-%d'),
            _export_status(record),
        ])

    # Auto-size columns (capped at 35 chars wide).
    for column_cells in sheet.columns:
        max_length = max(len(str(cell.value or '')) for cell in column_cells)
        sheet.column_dimensions[get_column_letter(column_cells[0].column)].width = min(max_length + 2, 35)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    suffix = f'_{month_value}' if month_value else ''
    response['Content-Disposition'] = f'attachment; filename="attendance_records{suffix}.xlsx"'
    workbook.save(response)
    return response
