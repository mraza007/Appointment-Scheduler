from django.db import models

# Create your models here.

class appointments(models.Model):
	first_name = models.CharField(max_length=200)
	last_name  = models.CharField(max_length=200)
	email = models.EmailField(max_length=100,blank=True)
	appointment_title = models.CharField(max_length=40)
	appointment_description = models.TextField()
	time_field = models.TimeField(blank=True, null=True)
	date_field = models.DateField(blank=True, null=True)
	address = models.CharField(max_length=250)
	state = models.CharField(max_length=5)
	city = models.CharField(max_length=50)
	zip_code = models.CharField(max_length=6)
	phone = models.CharField(max_length=14)
	notes = models.TextField()


	def __str__(self):
		return self.appointment_title


