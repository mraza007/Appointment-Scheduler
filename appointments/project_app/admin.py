from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin interface for Appointment model."""

    list_display = [
        'appointment_title',
        'full_name',
        'email',
        'date_field',
        'time_field',
        'status',
        'owner',
        'created_at'
    ]
    list_filter = ['status', 'date_field', 'created_at']
    search_fields = [
        'first_name',
        'last_name',
        'email',
        'appointment_title',
        'appointment_description'
    ]
    ordering = ['-date_field', '-time_field']
    date_hierarchy = 'date_field'

    fieldsets = (
        ('Contact Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Appointment Details', {
            'fields': ('appointment_title', 'appointment_description', 'status')
        }),
        ('Schedule', {
            'fields': ('date_field', 'time_field')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'zip_code')
        }),
        ('Additional', {
            'fields': ('notes', 'owner'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Name'
