""" 'Home' URL Configuration
    - Configuration for the default home page
"""

from django.conf.urls import url

from . import views

urlpatterns= [
    url(r'^$', views.index, name='index'),
]
