from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from mailing_service.forms import StyleFormMixin
from users.models import User


class UserRegistrationForm(StyleFormMixin, UserCreationForm):
    """Форма для регистрации"""

    class Meta:
        model = User
        fields = ("email", "phone_number", "avatar", "country", "password1", "password2")


class UserProfileForm(StyleFormMixin, ModelForm):
    """Форма для регистрации"""

    class Meta:
        model = User
        fields = ("email", "phone_number", "avatar", "country")
