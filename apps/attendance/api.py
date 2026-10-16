"""Role-scoped JSON endpoints for dashboard data and attendance workflows."""

import json

from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from events.models import Event
from users.api import api_role_required
from users.models import CustomUser
from .forms import AttendanceRequestForm
from .models import AttendanceRequest


def request_payload(item):
    student = item.student
    return {
        'id': item.pk,
        'event': item.display_event_name,
        'event_type': item.event_type,
        'event_type_label': item.get_event_type_display(),
        'date': item.display_event_date.isoformat() if item.display_event_date else '',
        'time': item.display_event_time.strftime('%H:%M') if item.display_event_time else '',
        'venue': item.display_event_venue,
        'reason': item.reason,
        'status': item.status,
        'status_label': item.get_status_display(),
        'created_at': timezone.localtime(item.created_at).isoformat(),
        'student': {
            'id': student.pk,
            'name': student.get_full_name() or student.username,
            'username': student.username,
            'department': student.department,
            'division': student.get_division_display() if student.division else '',
            'student_id': student.student_id,
        },
        'coordinator': (
            item.coordinator.get_full_name() or item.coordinator.username
            if item.coordinator else ''
        ),
        'attendance': item.is_attended,
        'coordinator_remarks': item.coordinator_remarks,
        'teacher_remarks': item.teacher_remarks,
    }


def _month_filter(queryset, value):
    if not value:
        return queryset, None
    try:
        month = int(value)
    except (TypeError, ValueError):
        return None, 'Month must be a number from 1 to 12.'
    if not 1 <= month <= 12:
        return None, 'Month must be a number from 1 to 12.'
    return queryset.filter(created_at__month=month), None


@require_GET
@api_role_required(
    CustomUser.Role.STUDENT,
    CustomUser.Role.COORDINATOR,
    CustomUser.Role.TEACHER,
)
def dashboard(request):
    user = request.user
    role = user.role
    queryset = AttendanceRequest.objects.select_related(
        'student', 'event', 'coordinator', 'teacher'
    )
    if role == CustomUser.Role.STUDENT:
        queryset = queryset.filter(student=user)
    elif role == CustomUser.Role.COORDINATOR:
        queryset = queryset.filter(
            event__organizer=user,
            event_type=AttendanceRequest.EventType.COORDINATOR,
        )
    else:
        queryset = queryset.filter(student__division=user.division)

    month = request.GET.get('month', '')
    if role == CustomUser.Role.TEACHER and month:
        queryset, error = _month_filter(queryset, month)
        if error:
            return JsonResponse({'error': error}, status=400)

    if role == CustomUser.Role.STUDENT:
        stats = {
            'total': queryset.count(),
            'pending': queryset.filter(status=AttendanceRequest.Status.PENDING).count(),
            'in_progress': queryset.filter(status=AttendanceRequest.Status.COORDINATOR_APPROVED).count(),
            'approved': queryset.filter(status=AttendanceRequest.Status.TEACHER_APPROVED).count(),
            'rejected': queryset.filter(status__in=[
                AttendanceRequest.Status.COORDINATOR_REJECTED,
                AttendanceRequest.Status.TEACHER_REJECTED,
            ]).count(),
        }
        default_statuses = list(AttendanceRequest.Status.values)
    elif role == CustomUser.Role.COORDINATOR:
        stats = {
            'pending': queryset.filter(status=AttendanceRequest.Status.PENDING).count(),
            'approved': queryset.filter(status=AttendanceRequest.Status.COORDINATOR_APPROVED).count(),
            'rejected': queryset.filter(status=AttendanceRequest.Status.COORDINATOR_REJECTED).count(),
            'total': queryset.count(),
        }
        default_statuses = [
            AttendanceRequest.Status.PENDING,
            AttendanceRequest.Status.COORDINATOR_APPROVED,
            AttendanceRequest.Status.COORDINATOR_REJECTED,
        ]
    else:
        stats = {
            'awaiting': queryset.filter(status=AttendanceRequest.Status.COORDINATOR_APPROVED).count(),
            'approved': queryset.filter(status=AttendanceRequest.Status.TEACHER_APPROVED).count(),
            'rejected': queryset.filter(status=AttendanceRequest.Status.TEACHER_REJECTED).count(),
            'attended': queryset.filter(is_attended=True).count(),
        }
        default_statuses = [
            AttendanceRequest.Status.COORDINATOR_APPROVED,
            AttendanceRequest.Status.TEACHER_APPROVED,
            AttendanceRequest.Status.TEACHER_REJECTED,
        ]

    status = request.GET.get('status', '')
    filtered = queryset
    if status == 'rejected':
        filtered = filtered.filter(status__in=[
            AttendanceRequest.Status.COORDINATOR_REJECTED,
            AttendanceRequest.Status.TEACHER_REJECTED,
        ])
    elif status:
        status_aliases = {
            'in_progress': AttendanceRequest.Status.COORDINATOR_APPROVED,
            'awaiting': AttendanceRequest.Status.COORDINATOR_APPROVED,
            'approved': (
                AttendanceRequest.Status.COORDINATOR_APPROVED
                if role == CustomUser.Role.COORDINATOR
                else AttendanceRequest.Status.TEACHER_APPROVED
            ),
        }
        resolved_status = status_aliases.get(status, status)
        valid_statuses = {value for value, _label in AttendanceRequest.Status.choices}
        if resolved_status not in valid_statuses:
            return JsonResponse({'error': 'Unknown request status filter.'}, status=400)
        filtered = filtered.filter(status=resolved_status)
    else:
        filtered = filtered.filter(status__in=default_statuses)

    response = {
        'stats': stats,
        'requests': [request_payload(item) for item in filtered[:100]],
        'month': month,
    }
    if role == CustomUser.Role.STUDENT:
        response['events'] = [
            {
                'id': event.pk,
                'name': event.name,
                'date': event.date.isoformat(),
                'time': event.time.strftime('%H:%M'),
                'venue': event.venue,
            }
            for event in Event.objects.filter(is_active=True)
        ]
    elif role == CustomUser.Role.COORDINATOR:
        response['events'] = [
            {
                'id': event.pk,
                'name': event.name,
                'date': event.date.isoformat(),
                'time': event.time.strftime('%H:%M'),
                'venue': event.venue,
            }
            for event in Event.objects.filter(organizer=user)[:5]
        ]
    else:
        activity_query = CustomUser.objects.filter(
            role=CustomUser.Role.STUDENT,
            division=user.division,
            attendance_requests__isnull=False,
        )
        if month:
            activity_query = activity_query.filter(attendance_requests__created_at__month=int(month))
        response['student_activity'] = list(
            activity_query.annotate(
                total=Count('attendance_requests', distinct=True),
                pending=Count(
                    'attendance_requests',
                    filter=Q(attendance_requests__status__in=[
                        AttendanceRequest.Status.PENDING,
                        AttendanceRequest.Status.COORDINATOR_APPROVED,
                    ]),
                    distinct=True,
                ),
                approved=Count(
                    'attendance_requests',
                    filter=Q(attendance_requests__status=AttendanceRequest.Status.TEACHER_APPROVED),
                    distinct=True,
                ),
                rejected=Count(
                    'attendance_requests',
                    filter=Q(attendance_requests__status__in=[
                        AttendanceRequest.Status.COORDINATOR_REJECTED,
                        AttendanceRequest.Status.TEACHER_REJECTED,
                    ]),
                    distinct=True,
                ),
            ).order_by('-total', 'student_id', 'first_name')[:30].values(
                'id', 'first_name', 'last_name', 'username', 'student_id',
                'total', 'pending', 'approved', 'rejected',
            )
        )
        response['teacher_division'] = (
            user.get_division_display() if user.division else 'Not Assigned'
        )
    return JsonResponse(response)


@require_POST
@api_role_required(CustomUser.Role.STUDENT)
def create_request(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON request.'}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({'error': 'Expected a request object.'}, status=400)
    form = AttendanceRequestForm(data)
    if not form.is_valid():
        return JsonResponse(
            {'error': 'Please correct the request details.', 'fields': form.errors.get_json_data()},
            status=400,
        )
    event = form.cleaned_data.get('event')
    if event and AttendanceRequest.objects.filter(student=request.user, event=event).exists():
        return JsonResponse({'error': 'You already submitted a request for this event.'}, status=409)
    item = form.save(commit=False)
    item.student = request.user
    if item.event_type == AttendanceRequest.EventType.OPEN:
        item.status = AttendanceRequest.Status.COORDINATOR_APPROVED
    item.save()
    return JsonResponse({'request': request_payload(item)}, status=201)


@require_POST
@api_role_required(CustomUser.Role.COORDINATOR, CustomUser.Role.TEACHER)
def review_request(request, pk):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON request.'}, status=400)
    if not isinstance(data, dict) or data.get('action') not in {'approve', 'reject'}:
        return JsonResponse({'error': 'Choose approve or reject.'}, status=400)

    item_query = AttendanceRequest.objects.select_related('student', 'event')
    if request.user.role == CustomUser.Role.COORDINATOR:
        item_query = item_query.filter(
            event__organizer=request.user,
            event_type=AttendanceRequest.EventType.COORDINATOR,
            status=AttendanceRequest.Status.PENDING,
        )
    else:
        item_query = item_query.filter(
            student__division=request.user.division,
            status=AttendanceRequest.Status.COORDINATOR_APPROVED,
        )
    item = item_query.filter(pk=pk).first()
    if item is None:
        return JsonResponse({'error': 'This request is not available for review.'}, status=404)

    remarks = data.get('remarks', '')
    if not isinstance(remarks, str) or len(remarks) > 10000:
        return JsonResponse({'error': 'Reviewer remarks are invalid.'}, status=400)
    if request.user.role == CustomUser.Role.COORDINATOR:
        item.coordinator = request.user
        item.coordinator_remarks = remarks
        item.coordinator_action_at = timezone.now()
        item.status = (
            AttendanceRequest.Status.COORDINATOR_APPROVED
            if data['action'] == 'approve'
            else AttendanceRequest.Status.COORDINATOR_REJECTED
        )
    else:
        item.teacher = request.user
        item.teacher_remarks = remarks
        item.teacher_action_at = timezone.now()
        item.status = (
            AttendanceRequest.Status.TEACHER_APPROVED
            if data['action'] == 'approve'
            else AttendanceRequest.Status.TEACHER_REJECTED
        )
    item.save()
    return JsonResponse({'request': request_payload(item)})


@require_POST
@api_role_required(CustomUser.Role.TEACHER)
def mark_attendance(request, pk):
    item = AttendanceRequest.objects.filter(
        pk=pk,
        student__division=request.user.division,
        status=AttendanceRequest.Status.TEACHER_APPROVED,
    ).select_related('student', 'event').first()
    if item is None:
        return JsonResponse({'error': 'Only approved requests in your division can be marked attended.'}, status=404)
    item.is_attended = True
    item.save(update_fields=['is_attended', 'updated_at'])
    return JsonResponse({'request': request_payload(item)})
