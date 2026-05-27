from django.contrib.auth.forms import UserCreationForm
from mailing_service.forms import StyleFormMixin

from users.models import User



class UserRegistrationForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "phone_number", "avatar", "country", "password1", "password2")
