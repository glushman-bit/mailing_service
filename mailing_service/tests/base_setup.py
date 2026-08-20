from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from mailing_service.models import Mailing, Message, Recipient
from users.models import User


class BaseDataTest(TestCase):
    """Класс проверки получателей рассылки."""

    @classmethod
    def setUpTestData(cls):

        cls.user1 = User.objects.create(email="user1@test.com")
        cls.user1.set_password("TestPass123!")
        cls.user1.save()

        cls.user2 = User.objects.create(email="user2@test.com")
        cls.user2.set_password("TestPass123!")
        cls.user2.save()

        cls.manager = User.objects.create(email="mansger@test.com")
        cls.manager.set_password("TestPass123!")
        cls.manager.is_staff = True
        cls.manager.save()

        cls.admin = User.objects.create(email="admin@test.com")
        cls.admin.set_password("TestPass123!")
        cls.admin.is_superuser = True
        cls.admin.is_staff = True
        cls.admin.save()

        cls.recipient1 = Recipient.objects.create(
            email="recipient1@test.com",
            full_name="User One",
            comment="Test",
            owner=cls.user1,
        )

        cls.recipient2 = Recipient.objects.create(
            email="recipient2@test.com",
            full_name="User Two",
            comment="Test",
            owner=cls.user2,
        )

        cls.message1 = Message.objects.create(
            title="Сообщение пользователя",
            content="Текст сообщения пользователя",
            owner=cls.user1,
        )

        cls.message2 = Message.objects.create(
            title="Сообщение другого пользователя",
            content="Текст другого пользователя",
            owner=cls.user2,
        )

        cls.mailing1 = Mailing.objects.create(
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2),
            message=cls.message1,
            owner=cls.user1,
        )

        cls.mailing2 = Mailing.objects.create(
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2),
            message=cls.message2,
            owner=cls.user2,
        )
