from django.shortcuts import render
from django.template.response import TemplateResponse
from project_app.models import appointments
from django.views.generic.base import TemplateView
from django.views.generic import DetailView
from .forms import appointmentForm
from django.shortcuts import redirect
from django.shortcuts import get_list_or_404, get_object_or_404



# Create your views here.



class appointmentsdetail(DetailView):
	template_name = 'appointment_files/view_appointment.html'
	model = appointments
    
def appoint_remove(request, pk):
    appointments_model = get_object_or_404(appointments, pk=pk)
    appointments_model.delete()
    return redirect('view')
  
def index(request):
	return render(request, 'appointment_files/index.html')

def appointment(request):
	return render(request, 'appointment_files/appointment.html')

def view(request):
	data = appointments.objects.all()
	return TemplateResponse(request, 'appointment_files/view.html' , {"data": data})


def post_new(request):
	if request.method == "POST":
		form = appointmentForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.save()
			return redirect('appointmentsdetail',pk=post.pk)
	else:
		form=appointmentForm()
		return render(request, 'appointment_files/appointments_form.html',{'form':form})

	
	  








