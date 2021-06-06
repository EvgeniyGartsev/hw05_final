# here wrote forms based models
# import base form for registration new user
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class CreationForm(UserCreationForm):
    '''Create form for registration new users,
       base UserCreationForm'''
    class Meta(UserCreationForm.Meta):
        model = User  # form link model user
        fields = ["first_name", "last_name", "username", "email"]
