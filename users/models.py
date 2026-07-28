import os.path

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from config import settings


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True,
        verbose_name="email",
    )
    phone_number = PhoneNumberField(
        verbose_name="Номер телефона",
        region="RU",
        blank=True,
        null=True,
        help_text="Введите номер телефона",
    )
    avatar = models.ImageField(
        upload_to="users/avatar",
        verbose_name="Avatar", 
        blank=True,
        null=True,
        help_text="Загрузить аватар"
    )
    country = CountryField(
        blank_label="Country",
        help_text="Выберите страну",
        blank=True,
        null=True,
    )
    token = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Token",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email

    @property
    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return f"/{settings.STATIC_URL.lstrip("/")}avatar/default-avatar.jpg"
