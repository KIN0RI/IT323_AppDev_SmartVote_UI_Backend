from django.urls import path
from .views import LoginView, register, profile, login_with_email

urlpatterns = [
    path('login/',        LoginView.as_view(), name='login'),
    path('login-email/',  login_with_email,    name='login-email'),
    path('register/',     register,            name='register'),
    path('profile/',      profile,             name='profile'),
]
