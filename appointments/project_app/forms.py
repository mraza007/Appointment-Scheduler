from django import forms
from .models import appointments

class appointmentForm(forms.ModelForm):
	class Meta:
		model = appointments
		fields = 	('first_name', 'last_name' ,'email' , 'appointment_title'  , 'appointment_description'  , 
			'time_field' ,'date_field' ,'address'  ,'state'  ,'city'  ,'zip_code'  ,'phone'  ,'notes')  




