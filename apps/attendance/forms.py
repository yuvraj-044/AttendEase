"""Forms for attendance request submission and review."""

from django import forms
from .models import AttendanceRequest
from events.models import Event


class AttendanceRequestForm(forms.ModelForm):
    """Form for students to submit event attendance requests."""

    event = forms.ModelChoiceField(
        queryset=Event.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text='Select the college event you want to attend.'
    )

    class Meta:
        model = AttendanceRequest
        fields = [
            'event_type', 'event', 'external_event_name',
            'external_college_name', 'external_event_location',
            'external_event_date', 'external_event_time', 'reason',
        ]
        widgets = {
            'event_type': forms.RadioSelect(attrs={
                'class': 'form-check-input',
            }),
            'external_event_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter external event name',
            }),
            'external_college_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter host college name',
            }),
            'external_event_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter venue or city',
            }),
            'external_event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'external_event_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Explain why you want to attend this event...',
                'rows': 4,
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        event_type = cleaned_data.get('event_type')

        if event_type == AttendanceRequest.EventType.OPEN:
            cleaned_data['event'] = None
            required_fields = [
                ('external_event_name', 'Enter the external event name.'),
                ('external_college_name', 'Enter the host college name.'),
                ('external_event_location', 'Enter the event location.'),
                ('external_event_date', 'Enter the event date.'),
                ('external_event_time', 'Enter the event time.'),
            ]
            for field_name, message in required_fields:
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, message)
        else:
            if not cleaned_data.get('event'):
                self.add_error('event', 'Select a college event.')
            for field_name in [
                'external_event_name', 'external_college_name',
                'external_event_location', 'external_event_date',
                'external_event_time',
            ]:
                cleaned_data[field_name] = None if field_name.endswith(('_date', '_time')) else ''

        return cleaned_data


class ReviewForm(forms.Form):
    """Form for coordinators/teachers to add remarks when reviewing requests."""

    remarks = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Add your remarks (optional)...',
            'rows': 3,
        }),
        required=False,
    )
