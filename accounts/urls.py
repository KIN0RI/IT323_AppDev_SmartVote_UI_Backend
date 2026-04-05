from django.urls import path
from .views import LoginView, register, profile

urlpatterns = [
    path('login/',    LoginView.as_view(), name='login'),
    path('register/', register,            name='register'),
    path('profile/',  profile,             name='profile'),
]