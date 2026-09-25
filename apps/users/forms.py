"""
User registration and authentication forms.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

ALLOWED_EMAIL_DOMAIN = 'pccoepune.org'


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
            'role', 'division', 'grade', 'student_id', 'department', 'phone',
            'password1', 'password2',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@pccoepune.org'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'division': forms.Select(attrs={'class': 'form-select', 'id': 'id_division'}),
            'grade': forms.Select(attrs={'class': 'form-select', 'id': 'id_grade'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Roll number / ID'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Engineering'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['grade'].required = False
        # Style the password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password',
        })

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if not email.endswith(f'@{ALLOWED_EMAIL_DOMAIN}'):
            raise forms.ValidationError(f'Use your @{ALLOWED_EMAIL_DOMAIN} email address.')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class CustomLoginForm(AuthenticationForm):
    """Styled login form."""

    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username or PCCOE email',
        'autofocus': True,
        'id': 'id_login_username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
        'id': 'id_login_password',
    }))

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()
        if '@' in username:
            if not username.lower().endswith(f'@{ALLOWED_EMAIL_DOMAIN}'):
                raise forms.ValidationError(f'Use your @{ALLOWED_EMAIL_DOMAIN} email address.')
            try:
                user = CustomUser.objects.get(email__iexact=username)
                return user.get_username()
            except CustomUser.DoesNotExist:
                return username
        return username
