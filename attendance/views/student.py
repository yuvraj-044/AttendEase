"""
Student-facing views.

  student_dashboard     — overview of all submitted requests + stats
  submit_request        — form to submit a new attendance request
  request_detail        — read-only detail view of a single request
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from users.decorators import role_required
from ..models import AttendanceRequest
from ..forms import AttendanceRequestForm


@role_required('student')
def student_dashboard(request):
    """Student dashboard showing stats and recent requests."""
    requests = AttendanceRequest.objects.filter(student=request.user)

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

            # Prevent duplicate requests for internal coordinator events.
            if (
                event_type == AttendanceRequest.EventType.COORDINATOR
                and AttendanceRequest.objects.filter(student=request.user, event=event).exists()
            ):
                messages.warning(request, 'You have already submitted a request for this event.')
                return redirect('attendance:student_dashboard')

            att_request = form.save(commit=False)
            att_request.student = request.user

            # Open events skip the coordinator step and go straight to the teacher.
            if att_request.event_type == AttendanceRequest.EventType.OPEN:
                att_request.status = AttendanceRequest.Status.COORDINATOR_APPROVED

            att_request.save()

            if att_request.event_type == AttendanceRequest.EventType.OPEN:
                messages.success(
                    request,
                    f'Your open event request for "{att_request.display_event_name}" '
                    'has been sent directly to your class teacher.'
                )
            else:
                messages.success(
                    request,
                    f'Your attendance request for "{att_request.display_event_name}" has been submitted!'
                )
            return redirect('attendance:student_dashboard')
    else:
        form = AttendanceRequestForm()

    return render(request, 'attendance/submit_request.html', {'form': form})


@role_required('student')
def request_detail(request, pk):
    """Student views the detail of one of their own requests."""
    att_request = get_object_or_404(AttendanceRequest, pk=pk, student=request.user)
    return render(request, 'attendance/request_detail.html', {
        'att_request': att_request,
        'role': 'student',
    })
