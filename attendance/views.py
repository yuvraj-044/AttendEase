"""
Attendance views for all three roles.
- Student: dashboard, submit request, view history
- Coordinator: dashboard, review pending requests, approve/reject
- Teacher: dashboard, review coordinator-approved requests, approve/reject, mark attendance
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Count, Q
from datetime import time

from users.decorators import role_required
from .models import AttendanceRequest
from .forms import AttendanceRequestForm, ReviewForm
from events.models import Event
from users.models import CustomUser

MONTH_CHOICES = [
    ('', 'All Months'),
    ('1', 'January'),
    ('2', 'February'),
    ('3', 'March'),
    ('4', 'April'),
    ('5', 'May'),
    ('6', 'June'),
    ('7', 'July'),
    ('8', 'August'),
    ('9', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December'),
]


# ──────────────────────────────────────────────
# STUDENT VIEWS
# ──────────────────────────────────────────────

@role_required('student')
def student_dashboard(request):
    """Student dashboard showing stats and recent requests."""
    requests = AttendanceRequest.objects.filter(student=request.user)

    # Aggregate stats for dashboard cards
    stats = {
        'total': requests.count(),
        'pending': requests.filter(status=AttendanceRequest.Status.PENDING).count(),
        'approved': requests.filter(status=AttendanceRequest.Status.TEACHER_APPROVED).count(),
        'rejected': requests.filter(
            status__in=[
                AttendanceRequest.Status.COORDINATOR_REJECTED,
                AttendanceRequest.Status.TEACHER_REJECTED,
            ]
        ).count(),
        'in_progress': requests.filter(
            status=AttendanceRequest.Status.COORDINATOR_APPROVED
        ).count(),
    }

    # Filter support
    status_filter = request.GET.get('status', '')
    if status_filter:
        requests = requests.filter(status=status_filter)

    return render(request, 'attendance/student_dashboard.html', {
        'requests': requests[:20],
        'stats': stats,
        'status_filter': status_filter,
    })


@role_required('student')
def submit_request(request):
    """Allow students to submit an event attendance request."""
    if request.method == 'POST':
        form = AttendanceRequestForm(request.POST)
        if form.is_valid():
            event = form.cleaned_data['event']
            event_type = form.cleaned_data['event_type']

            # Check duplicate requests only for internal coordinator events.
            if (
                event_type == AttendanceRequest.EventType.COORDINATOR
                and AttendanceRequest.objects.filter(student=request.user, event=event).exists()
            ):
                messages.warning(request, 'You have already submitted a request for this event.')
                return redirect('attendance:student_dashboard')

            att_request = form.save(commit=False)
            att_request.student = request.user
            if att_request.event_type == AttendanceRequest.EventType.OPEN:
                att_request.status = AttendanceRequest.Status.COORDINATOR_APPROVED
            att_request.save()
            if att_request.event_type == AttendanceRequest.EventType.OPEN:
                messages.success(
                    request,
                    f'Your open event request for "{att_request.display_event_name}" has been sent directly to your class teacher.'
                )
            else:
                messages.success(request, f'Your attendance request for "{att_request.display_event_name}" has been submitted!')
            return redirect('attendance:student_dashboard')
    else:
        form = AttendanceRequestForm()

    return render(request, 'attendance/submit_request.html', {'form': form})


@role_required('student')
def request_detail_student(request, pk):
    """Student views detail of their own request."""
    att_request = get_object_or_404(AttendanceRequest, pk=pk, student=request.user)
    return render(request, 'attendance/request_detail.html', {
        'att_request': att_request,
        'role': 'student',
    })


# ──────────────────────────────────────────────
# COORDINATOR VIEWS
# ──────────────────────────────────────────────

@role_required('coordinator')
def coordinator_dashboard(request):
    """Coordinator dashboard showing pending student requests for their own events only."""
    # Only show coordinator-event requests for events created by this coordinator.
    all_requests = AttendanceRequest.objects.filter(
        event__organizer=request.user,
        event_type=AttendanceRequest.EventType.COORDINATOR,
    )

    stats = {
        'pending': all_requests.filter(status=AttendanceRequest.Status.PENDING).count(),
        'approved': all_requests.filter(status=AttendanceRequest.Status.COORDINATOR_APPROVED).count(),
        'rejected': all_requests.filter(status=AttendanceRequest.Status.COORDINATOR_REJECTED).count(),
        'total': all_requests.count(),
    }

    # Filter support
    status_filter = request.GET.get('status', '')
    if status_filter:
        requests = all_requests.filter(status=status_filter)
    else:
        # Default: show pending requests first
        requests = all_requests.filter(
            status__in=[
                AttendanceRequest.Status.PENDING,
                AttendanceRequest.Status.COORDINATOR_APPROVED,
                AttendanceRequest.Status.COORDINATOR_REJECTED,
            ]
        )

    # Get coordinator's events for quick stats
    my_events = Event.objects.filter(organizer=request.user)

    return render(request, 'attendance/coordinator_dashboard.html', {
        'requests': requests[:30],
        'stats': stats,
        'my_events': my_events[:5],
        'status_filter': status_filter,
    })


@role_required('coordinator')
def coordinator_review(request, pk):
    """Coordinator reviews and approves/rejects a pending request."""
    att_request = get_object_or_404(
        AttendanceRequest, pk=pk, status=AttendanceRequest.Status.PENDING,
        event_type=AttendanceRequest.EventType.COORDINATOR,
        event__organizer=request.user  # Only the event's coordinator can review
    )
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        action = request.POST.get('action')  # 'approve' or 'reject'

        if form.is_valid():
            att_request.coordinator = request.user
            att_request.coordinator_remarks = form.cleaned_data.get('remarks', '')
            att_request.coordinator_action_at = timezone.now()

            if action == 'approve':
                att_request.status = AttendanceRequest.Status.COORDINATOR_APPROVED
                messages.success(request, f'Request from {att_request.student} approved.')
            elif action == 'reject':
                att_request.status = AttendanceRequest.Status.COORDINATOR_REJECTED
                messages.warning(request, f'Request from {att_request.student} rejected.')

            att_request.save()
            return redirect('attendance:coordinator_dashboard')

    return render(request, 'attendance/review_request.html', {
        'att_request': att_request,
        'form': form,
        'role': 'coordinator',
        'title': 'Coordinator Review',
    })


# ──────────────────────────────────────────────
# TEACHER VIEWS
# ──────────────────────────────────────────────

@role_required('teacher')
def teacher_dashboard(request):
    """Teacher dashboard showing coordinator-approved requests from students in their division only."""
    # Only show requests from students in this teacher's division
    all_requests = AttendanceRequest.objects.filter(student__division=request.user.division)

    stats = {
        'awaiting': all_requests.filter(status=AttendanceRequest.Status.COORDINATOR_APPROVED).count(),
        'approved': all_requests.filter(status=AttendanceRequest.Status.TEACHER_APPROVED).count(),
        'rejected': all_requests.filter(status=AttendanceRequest.Status.TEACHER_REJECTED).count(),
        'attended': all_requests.filter(is_attended=True).count(),
    }

    # Filter support
    status_filter = request.GET.get('status', '')
    if status_filter:
        requests = all_requests.filter(status=status_filter)
    else:
        # Default: show coordinator-approved requests
        requests = all_requests.filter(
            status__in=[
                AttendanceRequest.Status.COORDINATOR_APPROVED,
                AttendanceRequest.Status.TEACHER_APPROVED,
                AttendanceRequest.Status.TEACHER_REJECTED,
            ]
        )

    student_activity = CustomUser.objects.filter(
        role=CustomUser.Role.STUDENT,
        division=request.user.division,
        attendance_requests__isnull=False,
    ).annotate(
        total_requests=Count('attendance_requests', distinct=True),
        pending_requests=Count(
            'attendance_requests',
            filter=Q(attendance_requests__status__in=[
                AttendanceRequest.Status.PENDING,
                AttendanceRequest.Status.COORDINATOR_APPROVED,
            ]),
            distinct=True,
        ),
        approved_requests=Count(
            'attendance_requests',
            filter=Q(attendance_requests__status=AttendanceRequest.Status.TEACHER_APPROVED),
            distinct=True,
        ),
        rejected_requests=Count(
            'attendance_requests',
            filter=Q(attendance_requests__status__in=[
                AttendanceRequest.Status.COORDINATOR_REJECTED,
                AttendanceRequest.Status.TEACHER_REJECTED,
            ]),
            distinct=True,
        ),
    ).order_by('-total_requests', 'student_id', 'first_name', 'username')

    export_month = request.GET.get('month', '')

    return render(request, 'attendance/teacher_dashboard.html', {
        'requests': requests[:30],
        'stats': stats,
        'status_filter': status_filter,
        'student_activity': student_activity[:30],
        'export_month': export_month,
        'month_choices': MONTH_CHOICES,
        'teacher_division': request.user.get_division_display() if request.user.division else 'Not Assigned',
    })


def _parse_month(value):
    if not value:
        return None, None
    try:
        month = int(value)
        if 1 <= month <= 12:
            return None, month
        return None, None
    except (TypeError, ValueError):
        return None, None


def _teacher_division_requests(user, month_value=''):
    """Return all attendance requests for the teacher's division, oldest event first."""
    requests = AttendanceRequest.objects.filter(
        student__division=user.division
    ).select_related(
        'student', 'event'
    )

    _, month = _parse_month(month_value)
    if month:
        requests = requests.filter(created_at__month=month)

    return sorted(
        requests,
        key=lambda req: (
            req.export_event_date,
            req.display_event_time or time.min,
            req.student.student_id or '',
            req.student.get_full_name() or req.student.username,
        )
    )


def _export_status(att_request):
    if att_request.status == AttendanceRequest.Status.TEACHER_APPROVED:
        return 'Approved'
    if att_request.status in [
        AttendanceRequest.Status.COORDINATOR_REJECTED,
        AttendanceRequest.Status.TEACHER_REJECTED,
    ]:
        return 'Rejected'
    return 'Pending'


@role_required('teacher')
def teacher_export_excel(request):
    """Download division attendance requests as an Excel workbook."""
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
    for att_request in _teacher_division_requests(request.user, month_value):
        sheet.append([
            att_request.student.get_full_name() or att_request.student.username,
            att_request.student.student_id or '',
            att_request.student.get_division_display() or att_request.student.division or '',
            att_request.display_event_name,
            att_request.get_event_type_display(),
            att_request.export_event_date.strftime('%Y-%m-%d'),
            _export_status(att_request),
        ])

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


@role_required('teacher')
def teacher_review(request, pk):
    """Teacher reviews coordinator-approved requests for final approval."""
    att_request = get_object_or_404(
        AttendanceRequest, pk=pk, status=AttendanceRequest.Status.COORDINATOR_APPROVED,
        student__division=request.user.division  # Only the student's division teacher can review
    )
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        action = request.POST.get('action')

        if form.is_valid():
            att_request.teacher = request.user
            att_request.teacher_remarks = form.cleaned_data.get('remarks', '')
            att_request.teacher_action_at = timezone.now()

            if action == 'approve':
                att_request.status = AttendanceRequest.Status.TEACHER_APPROVED
                messages.success(request, f'Request from {att_request.student} approved.')
            elif action == 'reject':
                att_request.status = AttendanceRequest.Status.TEACHER_REJECTED
                messages.warning(request, f'Request from {att_request.student} rejected.')

            att_request.save()
            return redirect('attendance:teacher_dashboard')

    return render(request, 'attendance/review_request.html', {
        'att_request': att_request,
        'form': form,
        'role': 'teacher',
        'title': 'Teacher Review',
    })


@role_required('teacher')
def mark_attendance(request, pk):
    """Teacher marks that a student actually attended the event."""
    att_request = get_object_or_404(
        AttendanceRequest, pk=pk, status=AttendanceRequest.Status.TEACHER_APPROVED,
        student__division=request.user.division  # Only the student's division teacher can mark
    )

    if request.method == 'POST':
        att_request.is_attended = True
        att_request.save()
        messages.success(
            request,
            f'Attendance marked for {att_request.student} at "{att_request.display_event_name}".'
        )
        return redirect('attendance:teacher_dashboard')

    return render(request, 'attendance/mark_attendance.html', {
        'att_request': att_request,
    })
