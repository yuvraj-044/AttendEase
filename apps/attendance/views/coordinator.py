"""
Coordinator-facing views.

  coordinator_dashboard — pending requests for the coordinator's own events
  coordinator_review    — approve or reject a single pending request
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from users.decorators import role_required
from ..models import AttendanceRequest
from ..forms import ReviewForm
from events.models import Event


@role_required('coordinator')
def coordinator_dashboard(request):
    """
    Coordinator dashboard.
    Only shows requests for events this coordinator organises.
    """
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

    status_filter = request.GET.get('status', '')
    if status_filter:
        requests = all_requests.filter(status=status_filter)
    else:
        requests = all_requests.filter(
            status__in=[
                AttendanceRequest.Status.PENDING,
                AttendanceRequest.Status.COORDINATOR_APPROVED,
                AttendanceRequest.Status.COORDINATOR_REJECTED,
            ]
        )

    my_events = Event.objects.filter(organizer=request.user)

    return render(request, 'attendance/coordinator_dashboard.html', {
        'requests': requests[:30],
        'stats': stats,
        'my_events': my_events[:5],
        'status_filter': status_filter,
    })


@role_required('coordinator')
def coordinator_review(request, pk):
    """Coordinator approves or rejects a pending student request."""
    att_request = get_object_or_404(
        AttendanceRequest,
        pk=pk,
        status=AttendanceRequest.Status.PENDING,
        event_type=AttendanceRequest.EventType.COORDINATOR,
        event__organizer=request.user,  # Only the event's own coordinator may act.
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
