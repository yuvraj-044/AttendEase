"""Forms for creating and managing events."""

from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    """Form for coordinators to create/edit events."""

    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'venue', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the event...',
                'rows': 4,
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control date-picker',
                'type': 'text',
                'placeholder': 'Select date',
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control time-picker',
                'type': 'text',
                'placeholder': 'Select time',
            }),
            'venue': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event location',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
