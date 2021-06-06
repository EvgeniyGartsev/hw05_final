from django.urls import path

from . import views

urlpatterns = [
    # signup fo registration new users
    path("signup/", views.SignUp.as_view(), name="signup"),
]
