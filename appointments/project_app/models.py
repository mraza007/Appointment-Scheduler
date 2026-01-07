from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils import timezone


class Appointment(models.Model):
    """Model representing an appointment."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    zip_regex = RegexValidator(
        regex=r'^\d{5}(-\d{4})?$',
        message="ZIP code must be in format: 12345 or 12345-6789"
    )

    # Owner (for user authentication)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        null=True,
        blank=True
    )

    # Personal Information
    first_name = models.CharField(max_length=200, validators=[MinLengthValidator(2)])
    last_name = models.CharField(max_length=200, validators=[MinLengthValidator(2)])
    email = models.EmailField(max_length=100, blank=True)
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    # Appointment Details
    appointment_title = models.CharField(max_length=100)
    appointment_description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Scheduling
    time_field = models.TimeField(blank=True, null=True)
    date_field = models.DateField(blank=True, null=True)

    # Location
    address = models.CharField(max_length=250, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)

    # Additional
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_field', '-time_field']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'

    def __str__(self):
        return f"{self.appointment_title} - {self.date_field}"

    @property
    def is_past_due(self):
        """Check if the appointment date has passed."""
        if self.date_field:
            return self.date_field < timezone.now().date()
        return False

    @property
    def full_name(self):
        """Return the full name of the appointment contact."""
        return f"{self.first_name} {self.last_name}"


# Keep backwards compatibility alias
appointments = Appointment
