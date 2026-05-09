"""
User registration and authentication forms.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Registration form with role selection and additional profile fields."""

    role = forms.ChoiceField(
        choices=CustomUser.Role.choices,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_role',
        }),
        help_text='Select your role in the institution.'
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role', 'division', 'student_id', 'department', 'phone',
            'password1', 'password2',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'division': forms.Select(attrs={'class': 'form-select', 'id': 'id_division'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Roll number / ID'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Engineering'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password',
        })


class CustomLoginForm(AuthenticationForm):
    """Styled login form."""

    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
        'autofocus': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))
