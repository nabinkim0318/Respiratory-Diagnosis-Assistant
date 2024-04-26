from django.urls import path
from search import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('help/', views.help, name='help'),
    path('contact/', views.contact, name='contact'),
    path('submit/', views.submit, name='submit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
