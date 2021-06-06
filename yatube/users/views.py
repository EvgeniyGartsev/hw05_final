from django.views.generic import CreateView
# reverse_lazy allow take url by "name" in path("url/", view, name)
from django.urls import reverse_lazy

from .forms import CreationForm


class SignUp(CreateView):
    '''Class for registration users
    base on CreationForm'''
    form_class = CreationForm
    success_url = reverse_lazy("signup")
    template_name = "signup.html"
