from django.urls import path

from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("", views.landing, name="landing"),
    path("signup/", views.signup, name="signup"),
]



