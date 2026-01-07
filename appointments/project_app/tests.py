from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, time, timedelta
from .models import Appointment
from .forms import AppointmentForm, UserRegistrationForm


class AppointmentModelTests(TestCase):
    """Tests for the Appointment model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.appointment = Appointment.objects.create(
            owner=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890',
            appointment_title='Test Appointment',
            appointment_description='Test description',
            date_field=date.today() + timedelta(days=1),
            time_field=time(10, 0),
            address='123 Main St',
            city='Test City',
            state='TS',
            zip_code='12345',
            status='pending'
        )

    def test_appointment_creation(self):
        """Test that an appointment can be created."""
        self.assertEqual(self.appointment.first_name, 'John')
        self.assertEqual(self.appointment.last_name, 'Doe')
        self.assertEqual(self.appointment.status, 'pending')

    def test_appointment_str(self):
        """Test the string representation of an appointment."""
        expected = f"Test Appointment - {self.appointment.date_field}"
        self.assertEqual(str(self.appointment), expected)

    def test_full_name_property(self):
        """Test the full_name property."""
        self.assertEqual(self.appointment.full_name, 'John Doe')

    def test_is_past_due_property(self):
        """Test the is_past_due property."""
        # Future appointment
        self.assertFalse(self.appointment.is_past_due)

        # Past appointment
        self.appointment.date_field = date.today() - timedelta(days=1)
        self.appointment.save()
        self.assertTrue(self.appointment.is_past_due)

    def test_status_choices(self):
        """Test that status can be set to valid choices."""
        for status_value, _ in Appointment.STATUS_CHOICES:
            self.appointment.status = status_value
            self.appointment.save()
            self.assertEqual(self.appointment.status, status_value)


class AppointmentFormTests(TestCase):
    """Tests for the AppointmentForm."""

    def test_valid_form(self):
        """Test form with valid data."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'phone': '+1234567890',
            'appointment_title': 'Test Meeting',
            'appointment_description': 'A test meeting',
            'date_field': date.today() + timedelta(days=1),
            'time_field': time(14, 0),
            'address': '456 Oak Ave',
            'city': 'Test Town',
            'state': 'TT',
            'zip_code': '54321',
            'status': 'pending',
            'notes': 'Test notes'
        }
        form = AppointmentForm(data=data)
        self.assertTrue(form.is_valid())

    def test_past_date_validation(self):
        """Test that past dates are rejected."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'appointment_title': 'Test Meeting',
            'date_field': date.today() - timedelta(days=1),
            'status': 'pending',
        }
        form = AppointmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_field', form.errors)

    def test_short_first_name_validation(self):
        """Test that short first names are rejected."""
        data = {
            'first_name': 'J',
            'last_name': 'Doe',
            'appointment_title': 'Test Meeting',
            'status': 'pending',
        }
        form = AppointmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)


class UserRegistrationFormTests(TestCase):
    """Tests for the UserRegistrationForm."""

    def test_valid_registration(self):
        """Test form with valid registration data."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        form = UserRegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_duplicate_email_rejection(self):
        """Test that duplicate emails are rejected."""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='testpass123'
        )
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_mismatch(self):
        """Test that mismatched passwords are rejected."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass456!'
        }
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())


class ViewTests(TestCase):
    """Tests for views."""

    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.appointment = Appointment.objects.create(
            owner=self.user,
            first_name='John',
            last_name='Doe',
            appointment_title='Test Appointment',
            date_field=date.today() + timedelta(days=1),
            status='pending'
        )

    def test_index_view(self):
        """Test the index view."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointment_files/index.html')

    def test_view_appointments_list(self):
        """Test the appointments list view."""
        response = self.client.get(reverse('view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointment_files/view.html')

    def test_appointment_detail_view(self):
        """Test the appointment detail view."""
        response = self.client.get(
            reverse('appointmentsdetail', kwargs={'pk': self.appointment.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointment_files/view_appointment.html')

    def test_create_appointment_requires_login(self):
        """Test that creating an appointment requires login."""
        response = self.client.get(reverse('post_new'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_create_appointment_authenticated(self):
        """Test creating an appointment when authenticated."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('post_new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointment_files/appointments_form.html')

    def test_edit_appointment_requires_login(self):
        """Test that editing an appointment requires login."""
        response = self.client.get(
            reverse('appointment_edit', kwargs={'pk': self.appointment.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_delete_appointment_requires_login(self):
        """Test that deleting an appointment requires login."""
        response = self.client.get(
            reverse('appoint_remove', kwargs={'pk': self.appointment.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_calendar_view(self):
        """Test the calendar view."""
        response = self.client.get(reverse('calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointment_files/calendar.html')

    def test_search_appointments(self):
        """Test searching appointments."""
        response = self.client.get(reverse('view'), {'search': 'John'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John')

    def test_filter_by_status(self):
        """Test filtering appointments by status."""
        response = self.client.get(reverse('view'), {'status': 'pending'})
        self.assertEqual(response.status_code, 200)


class AuthenticationTests(TestCase):
    """Tests for authentication views."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_register_view_get(self):
        """Test GET request to register view."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointment_files/register.html')

    def test_register_view_post_valid(self):
        """Test valid registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view_get(self):
        """Test GET request to login view."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointment_files/login.html')

    def test_login_view_post_valid(self):
        """Test valid login."""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_logout_view(self):
        """Test logout functionality."""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout


class AppointmentCRUDTests(TestCase):
    """Tests for CRUD operations on appointments."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.appointment = Appointment.objects.create(
            owner=self.user,
            first_name='John',
            last_name='Doe',
            appointment_title='Test Appointment',
            date_field=date.today() + timedelta(days=1),
            status='pending'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_create_appointment(self):
        """Test creating a new appointment."""
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'appointment_title': 'New Appointment',
            'appointment_description': 'Test description',
            'date_field': date.today() + timedelta(days=2),
            'time_field': time(15, 0),
            'status': 'pending',
        }
        response = self.client.post(reverse('post_new'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(
            Appointment.objects.filter(appointment_title='New Appointment').exists()
        )

    def test_edit_appointment(self):
        """Test editing an existing appointment."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'appointment_title': 'Updated Appointment',
            'date_field': date.today() + timedelta(days=3),
            'status': 'confirmed',
        }
        response = self.client.post(
            reverse('appointment_edit', kwargs={'pk': self.appointment.pk}),
            data
        )
        self.assertEqual(response.status_code, 302)  # Redirect after update
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.appointment_title, 'Updated Appointment')
        self.assertEqual(self.appointment.status, 'confirmed')

    def test_delete_appointment(self):
        """Test deleting an appointment."""
        response = self.client.post(
            reverse('appoint_remove', kwargs={'pk': self.appointment.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect after delete
        self.assertFalse(
            Appointment.objects.filter(pk=self.appointment.pk).exists()
        )

    def test_update_status(self):
        """Test updating appointment status."""
        response = self.client.post(
            reverse('update_status', kwargs={'pk': self.appointment.pk}),
            {'status': 'confirmed'}
        )
        self.assertEqual(response.status_code, 200)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'confirmed')
