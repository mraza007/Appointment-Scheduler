from django.shortcuts import render
from django.template.response import TemplateResponse
from project_app.models import appointments
from django.views.generic.base import TemplateView
from django.views.generic import DetailView
from .forms import appointmentForm
from django.shortcuts import redirect



# Create your views here.



class appointmentsdetail(DetailView):
	template_name = 'appointment_files/view_appointment.html'
	model = appointments
    

  








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

	
	  


	   # form = appointmentForm(request.POST)
   	#    post = form.save(commit=False)
   	#    post.save()
    #    return redirect('appointmentsdetail', pk=post.pk)
   

# def appointmentsviewer(request):
# 	data = appointments.objects.only("last_name")
# 	return TemplateResponse(request, 'appointment_files/view_appointment.html' , {"data":data})

# class detailedview(generic.DetailView):
# 	model = appointments
# 	template = 'appointment_files/view_appointment.html'

# class indexview(generic.ListView):
# 		model = appointments
# 		template = 'appointment_files/view.html'
# 		context_object_name = 'all_appointments'
# 		def get_queryset(self):
# 			return appointments.objects.all()



# class indexview(generic.ListView):
# 		template = 'appointment_files/view.html'
# 		context_object_name = 'data'
# 		def get_queryset(self):
# 			return appointments.objects.all()






