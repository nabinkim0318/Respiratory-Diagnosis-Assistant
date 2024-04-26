from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from search import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('help/', views.help, name='help'),
    path('contact/', views.contact, name='contact'),
    path('submit/', views.submit, name='submit'),
]
