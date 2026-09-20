"""Views for event management (CRUD by coordinators)."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.decorators import role_required
from .models import Event
from .forms import EventForm


@login_required
def event_list(request):
    """List all active events (accessible to all authenticated users)."""
    events = Event.objects.filter(is_active=True)
    return render(request, 'events/event_list.html', {'events': events})


@role_required('coordinator')
def event_create(request):
    """Allow coordinators to create new events."""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, f'Event "{event.name}" created successfully!')
            return redirect('events:event_list')
    else:
        form = EventForm()

    return render(request, 'events/event_form.html', {
        'form': form,
        'title': 'Create Event',
    })


@role_required('coordinator')
def event_edit(request, pk):
    """Allow coordinators to edit their events."""
    event = get_object_or_404(Event, pk=pk, organizer=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.name}" updated successfully!')
            return redirect('events:event_list')
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {
        'form': form,
        'title': 'Edit Event',
        'event': event,
    })


@login_required
def event_detail(request, pk):
    """View event details."""
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})
