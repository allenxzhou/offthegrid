""" 'Events' URL Configuration
    - Configuration for the different event & vendor pages
"""

from django.conf.urls import url

from . import views

urlpatterns= [
    # Ex. /events/ -> default view of upcoming Off-The-Grid events
    url(r'^$', views.index, name='index'),
    # Ex. /events/vendors -> list of all vendors in descending occurrence count
    url(r'^vendors/$', views.vendors, name='vendors'),
    # Ex. /events/<event_name>/<event_date> -> specific event with its vendors
    url(r'^(?P<event_name>.*?)/(?P<event_date>[\d-]+?)$', views.details,
        name='details'),
    # Ex. /events/<vendor_name> -> specific vendor with its upcoming events
    url(r'^(?P<vendor_name>.*?)$', views.vendor, name='vendor'),
]