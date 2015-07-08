from django.conf.urls import url

from . import views

urlpatterns= [
    url(r'^$', views.index, name='index'),
    url(r'^vendors/$', views.vendors, name='vendors')
    url(r'^(?P<event_name>.*?)/(?P<event_date>[\d-]+?)$', views.details,
        name='details'),
    url(r'^(?P<vendor_name>.*?)$', views.vendor, name='vendor'),
]