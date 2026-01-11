from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse

from .models import Appointment
from .forms import AppointmentForm, UserRegistrationForm

import calendar
from datetime import datetime, date


# Home page
def index(request):
    """Display the home page."""
    return render(request, 'appointment_files/index.html')


# User Registration
def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Appointments App.')
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, 'appointment_files/register.html', {'form': form})


# List all appointments with search, filter, and pagination
def view(request):
    """
    Display all appointments with search, filter, and pagination.
    If user is authenticated, show only their appointments.
    """
    if request.user.is_authenticated:
        appointments_list = Appointment.objects.filter(owner=request.user)
    else:
        appointments_list = Appointment.objects.all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        appointments_list = appointments_list.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(appointment_title__icontains=search_query) |
            Q(appointment_description__icontains=search_query)
        )

    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments_list = appointments_list.filter(status=status_filter)

    # Date filter
    date_filter = request.GET.get('date', '')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            appointments_list = appointments_list.filter(date_field=filter_date)
        except ValueError:
            pass

    # Pagination
    paginator = Paginator(appointments_list, getattr(settings, 'APPOINTMENTS_PER_PAGE', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'data': page_obj,  # backwards compatibility
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'status_choices': Appointment.STATUS_CHOICES,
    }
    return TemplateResponse(request, 'appointment_files/view.html', context)


# Appointment Detail View
class AppointmentDetailView(DetailView):
    """Display detailed information about a single appointment."""
    template_name = 'appointment_files/view_appointment.html'
    model = Appointment
    context_object_name = 'appointments'  # backwards compatibility


# Create new appointment
@login_required
def post_new(request):
    """Handle creating a new appointment."""
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.owner = request.user
            appointment.save()

            # Send email notification
            send_appointment_notification(appointment, 'created')

            messages.success(request, 'Appointment created successfully!')
            return redirect('appointmentsdetail', pk=appointment.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm()

    return render(request, 'appointment_files/appointments_form.html', {'form': form})


# Edit existing appointment
@login_required
def appointment_edit(request, pk):
    """Handle editing an existing appointment."""
    appointment = get_object_or_404(Appointment, pk=pk)

    # Check ownership
    if appointment.owner and appointment.owner != request.user:
        messages.error(request, 'You do not have permission to edit this appointment.')
        return redirect('view')

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save()

            # Send email notification
            send_appointment_notification(appointment, 'updated')

            messages.success(request, 'Appointment updated successfully!')
            return redirect('appointmentsdetail', pk=appointment.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'appointment_files/appointments_form.html', {
        'form': form,
        'edit_mode': True,
        'appointment': appointment
    })


# Delete appointment
@login_required
def appoint_remove(request, pk):
    """Handle deleting an appointment."""
    appointment = get_object_or_404(Appointment, pk=pk)

    # Check ownership
    if appointment.owner and appointment.owner != request.user:
        messages.error(request, 'You do not have permission to delete this appointment.')
        return redirect('view')

    if request.method == "POST":
        appointment.delete()
        messages.success(request, 'Appointment deleted successfully!')
        return redirect('view')

    return render(request, 'appointment_files/confirm_delete.html', {
        'appointment': appointment
    })


# Update appointment status
@login_required
def update_status(request, pk):
    """Update the status of an appointment via AJAX."""
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk)

        # Check ownership
        if appointment.owner and appointment.owner != request.user:
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES):
            appointment.status = new_status
            appointment.save()

            # Send email notification for status change
            send_appointment_notification(appointment, 'status_changed')

            return JsonResponse({'success': True, 'status': appointment.get_status_display()})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


# Calendar View
def calendar_view(request):
    """Display appointments in a calendar view."""
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))

    # Get appointments for the month
    if request.user.is_authenticated:
        appointments = Appointment.objects.filter(
            owner=request.user,
            date_field__year=year,
            date_field__month=month
        )
    else:
        appointments = Appointment.objects.filter(
            date_field__year=year,
            date_field__month=month
        )

    # Create calendar
    cal = calendar.Calendar(firstweekday=6)  # Sunday start
    month_days = cal.monthdayscalendar(year, month)

    # Group appointments by date
    appointments_by_date = {}
    for appt in appointments:
        if appt.date_field:
            day = appt.date_field.day
            if day not in appointments_by_date:
                appointments_by_date[day] = []
            appointments_by_date[day].append(appt)

    # Navigation
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    context = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'month_days': month_days,
        'appointments_by_date': appointments_by_date,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'today': date.today(),
    }
    return render(request, 'appointment_files/calendar.html', context)


# Email notification helper
def send_appointment_notification(appointment, action):
    """Send email notification for appointment actions."""
    if not appointment.email:
        return

    subjects = {
        'created': f'New Appointment: {appointment.appointment_title}',
        'updated': f'Appointment Updated: {appointment.appointment_title}',
        'status_changed': f'Appointment Status Changed: {appointment.appointment_title}',
    }

    messages_content = {
        'created': f'''
Hello {appointment.first_name},

Your appointment has been created successfully.

Title: {appointment.appointment_title}
Date: {appointment.date_field}
Time: {appointment.time_field}
Status: {appointment.get_status_display()}

Thank you for using our Appointments App!
        ''',
        'updated': f'''
Hello {appointment.first_name},

Your appointment has been updated.

Title: {appointment.appointment_title}
Date: {appointment.date_field}
Time: {appointment.time_field}
Status: {appointment.get_status_display()}

Thank you for using our Appointments App!
        ''',
        'status_changed': f'''
Hello {appointment.first_name},

The status of your appointment has been changed.

Title: {appointment.appointment_title}
New Status: {appointment.get_status_display()}

Thank you for using our Appointments App!
        ''',
    }

    try:
        send_mail(
            subject=subjects.get(action, 'Appointment Notification'),
            message=messages_content.get(action, ''),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.email],
            fail_silently=True,
        )
    except Exception:
        pass  # Email sending is non-critical


# Legacy view for backwards compatibility
def appointment(request):
    """Legacy appointment view - redirects to list."""
    return redirect('view')


# Backwards compatibility aliases
appointmentsdetail = AppointmentDetailView
