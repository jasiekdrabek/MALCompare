from django.urls import path
from . import views

urlpatterns = [
path('', views.home, name='home'),
path('mal/login/', views.mal_login, name='mal_login'),
path('mal/callback/', views.mal_callback, name='mal_callback'),
path('fetch/<str:username>/save/', views.fetch_and_save, name='fetch_and_save'),
]
