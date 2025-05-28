
from django.urls import path
from . import views

app_name = 'users' # Define app_name for namespacing

urlpatterns = [
    path('register/', views.register, name='register'),
]