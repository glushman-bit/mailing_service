from django.contrib.auth.models import AbstractUser
from django.db import models
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


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
        upload_to="users/avatar", verbose_name="Avatar", blank=True, null=True, help_text="Загрузить аватар"
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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
