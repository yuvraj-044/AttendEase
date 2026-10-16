"""JSON event endpoints for the React application."""

import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from users.api import api_role_required
from users.models import CustomUser
from .forms import EventForm
from .models import Event


def event_payload(event):
    return {
        'id': event.pk,
        'name': event.name,
        'description': event.description,
        'date': event.date.isoformat(),
        'time': event.time.strftime('%H:%M'),
        'venue': event.venue,
        'organizer': event.organizer.get_full_name() or event.organizer.username,
    }


@require_http_methods(['GET', 'POST'])
@api_role_required()
def events(request):
    if request.method == 'GET':
        queryset = Event.objects.filter(is_active=True).select_related('organizer')
        if request.user.role == CustomUser.Role.COORDINATOR:
            queryset = queryset.filter(organizer=request.user)
        return JsonResponse({'events': [event_payload(event) for event in queryset]})

    if request.user.role != CustomUser.Role.COORDINATOR:
        return JsonResponse({'error': 'Only coordinators can create events.'}, status=403)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON request.'}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({'error': 'Expected an event object.'}, status=400)

    form = EventForm(data)
    if not form.is_valid():
        return JsonResponse({'error': 'Please correct the event details.', 'fields': form.errors.get_json_data()}, status=400)
    event = form.save(commit=False)
    event.organizer = request.user
    event.save()
    return JsonResponse({'event': event_payload(event)}, status=201)
