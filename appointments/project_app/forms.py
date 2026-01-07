from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    """Form for creating and editing appointments with validation."""

    class Meta:
        model = Appointment
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'appointment_title', 'appointment_description', 'status',
            'date_field', 'time_field',
            'address', 'city', 'state', 'zip_code',
            'notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number (e.g., +1234567890)'
            }),
            'appointment_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter appointment title'
            }),
            'appointment_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter appointment description'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date_field': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'time_field': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter state'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ZIP code (e.g., 12345)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes (optional)'
            }),
        }

    def clean_date_field(self):
        """Validate that appointment date is not in the past."""
        date_field = self.cleaned_data.get('date_field')
        if date_field and date_field < date.today():
            raise ValidationError('Appointment date cannot be in the past.')
        return date_field

    def clean_email(self):
        """Validate email format."""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
        return email

    def clean_first_name(self):
        """Clean and validate first name."""
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            first_name = first_name.strip().title()
            if len(first_name) < 2:
                raise ValidationError('First name must be at least 2 characters.')
        return first_name

    def clean_last_name(self):
        """Clean and validate last name."""
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            last_name = last_name.strip().title()
            if len(last_name) < 2:
                raise ValidationError('Last name must be at least 2 characters.')
        return last_name

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        date_field = cleaned_data.get('date_field')
        time_field = cleaned_data.get('time_field')

        # If both date and time are provided, ensure they're not in the past
        if date_field and time_field and date_field == date.today():
            from datetime import datetime
            current_time = timezone.now().time()
            if time_field < current_time:
                raise ValidationError(
                    'Appointment time cannot be in the past for today\'s date.'
                )

        return cleaned_data


class UserRegistrationForm(UserCreationForm):
    """Extended user registration form with email."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email').lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True):
        """Save user with email."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


# Backwards compatibility alias
appointmentForm = AppointmentForm
