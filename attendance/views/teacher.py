"""
Teacher-facing views.

  teacher_dashboard — coordinator-approved requests for the teacher's division
  teacher_review    — final approve / reject of a single request
  mark_attendance   — record that a student actually attended the event
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from users.decorators import role_required
from ..models import AttendanceRequest
from ..forms import ReviewForm
from users.models import CustomUser


# Month choices used by the dashboard filter and the export view.
MONTH_CHOICES = [
    ('', 'All Months'),
    ('1', 'January'), ('2', 'February'), ('3', 'March'),
    ('4', 'April'),   ('5', 'May'),       ('6', 'June'),
    ('7', 'July'),    ('8', 'August'),    ('9', 'September'),
    ('10', 'October'),('11', 'November'), ('12', 'December'),
]


@role_required('teacher')
def teacher_dashboard(request):
    """
    Teacher dashboard.
    Shows coordinator-approved requests from students in the teacher's division.
    Also surfaces a per-student activity breakdown.
    """
    all_requests = AttendanceRequest.objects.filter(
        student__division=request.user.division
    )

    stats = {
        'awaiting': all_requests.filter(status=AttendanceRequest.Status.COORDINATOR_APPROVED).count(),
        'approved': all_requests.filter(status=AttendanceRequest.Status.TEACHER_APPROVED).count(),
        'rejected': all_requests.filter(status=AttendanceRequest.Status.TEACHER_REJECTED).count(),
        'attended': all_requests.filter(is_attended=True).count(),
    }

    status_filter = request.GET.get('status', '')
    if status_filter:
        requests = all_requests.filter(status=status_filter)
    else:
        requests = all_requests.filter(
            status__in=[
                AttendanceRequest.Status.COORDINATOR_APPROVED,
                AttendanceRequest.Status.TEACHER_APPROVED,
                AttendanceRequest.Status.TEACHER_REJECTED,
            ]
        )

    student_activity = (
        CustomUser.objects
        .filter(
            role=CustomUser.Role.STUDENT,
            division=request.user.division,
            attendance_requests__isnull=False,
        )
        .annotate(
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
        )
        .order_by('-total_requests', 'student_id', 'first_name', 'username')
    )

    return render(request, 'attendance/teacher_dashboard.html', {
        'requests': requests[:30],
        'stats': stats,
        'status_filter': status_filter,
        'student_activity': student_activity[:30],
        'export_month': request.GET.get('month', ''),
        'month_choices': MONTH_CHOICES,
        'teacher_division': (
            request.user.get_division_display()
            if request.user.division
            else 'Not Assigned'
        ),
    })


@role_required('teacher')
def teacher_review(request, pk):
    """Teacher gives final approval or rejection to a coordinator-approved request."""
    att_request = get_object_or_404(
        AttendanceRequest,
        pk=pk,
        status=AttendanceRequest.Status.COORDINATOR_APPROVED,
        student__division=request.user.division,  # Only the student's own division teacher.
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
    """Teacher confirms that a student physically attended the approved event."""
    att_request = get_object_or_404(
        AttendanceRequest,
        pk=pk,
        status=AttendanceRequest.Status.TEACHER_APPROVED,
        student__division=request.user.division,  # Only the student's own division teacher.
    )

    if request.method == 'POST':
        att_request.is_attended = True
        att_request.save()
        messages.success(
            request,
            f'Attendance marked for {att_request.student} '
            f'at "{att_request.display_event_name}".'
        )
        return redirect('attendance:teacher_dashboard')

    return render(request, 'attendance/mark_attendance.html', {
        'att_request': att_request,
    })
