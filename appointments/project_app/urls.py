from django.conf.urls import url 
from . import views
from project_app.views import appointmentsdetail


urlpatterns = [
		url(r'^$',views.index ,name='index'),
		url(r'appointment/$',views.appointment ,name='appointment'),
		url(r'view/$',views.view,name='view'),
		url(r'appointmentsdetail/(?P<pk>\d+)$',views.appointmentsdetail.as_view() ,name='appointmentsdetail'),
		url(r'^post/new/$', views.post_new, name='post_new'),

]