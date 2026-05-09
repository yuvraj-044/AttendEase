"""Forms for attendance request submission and review."""

from django import forms
from .models import AttendanceRequest
from events.models import Event


class AttendanceRequestForm(forms.ModelForm):
    """Form for students to submit event attendance requests."""

    event = forms.ModelChoiceField(
        queryset=Event.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        help_text='Select the event you want to attend.'
    )

    class Meta:
        model = AttendanceRequest
        fields = ['event', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Explain why you want to attend this event...',
                'rows': 4,
            }),
        }


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
