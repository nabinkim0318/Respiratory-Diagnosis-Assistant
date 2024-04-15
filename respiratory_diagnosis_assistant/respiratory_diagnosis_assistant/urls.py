from django.urls import path
from search import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('help/', views.help, name='help'),
    path('contact/', views.contact, name='contact'),
    path('text-results/', views.text_results, name='text_results'),
    path('audio-results/', views.audio_results, name='audio_results'), 
]
