"""
Attendance views for all three roles.
- Student: dashboard, submit request, view history
- Coordinator: dashboard, review pending requests, approve/reject
- Teacher: dashboard, review coordinator-approved requests, approve/reject, mark attendance
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from users.decorators import role_required
from .models import AttendanceRequest
from .forms import AttendanceRequestForm, ReviewForm
from events.models import Event


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
            # Check for duplicate request
            event = form.cleaned_data['event']
            if AttendanceRequest.objects.filter(student=request.user, event=event).exists():
                messages.warning(request, 'You have already submitted a request for this event.')
                return redirect('attendance:student_dashboard')

            att_request = form.save(commit=False)
            att_request.student = request.user
            att_request.save()
            messages.success(request, f'Your attendance request for "{event.name}" has been submitted!')
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
    # Only show requests for events created by this coordinator
    all_requests = AttendanceRequest.objects.filter(event__organizer=request.user)

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

    return render(request, 'attendance/teacher_dashboard.html', {
        'requests': requests[:30],
        'stats': stats,
        'status_filter': status_filter,
        'teacher_division': request.user.get_division_display() if request.user.division else 'Not Assigned',
    })


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
            f'Attendance marked for {att_request.student} at "{att_request.event.name}".'
        )
        return redirect('attendance:teacher_dashboard')

    return render(request, 'attendance/mark_attendance.html', {
        'att_request': att_request,
    })
