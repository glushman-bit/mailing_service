from datetime import timedelta
from unittest.mock import patch

from django.core.cache import cache
from django.utils import timezone

from config import settings
from mailing_service.models import MailingAttempt
from mailing_service.services import get_cache, start_mailing
from mailing_service.tests.base_setup import BaseDataTest
from users.models import User


class StartMailingTest(BaseDataTest):
    """Тесты функции start_mailing."""

    @patch("mailing_service.services.send_mail")
    def test_start_mailing_success(self, mock_send_mail):
        """Успешная отправка писем всем получателям."""

        mailing = self.mailing1

        mailing.recipients.add(self.recipient1)

        mailing.start_time = timezone.now() - timedelta(minutes=5)
        mailing.end_time = timezone.now() + timedelta(minutes=5)
        mailing.save()

        mock_send_mail.return_value = 1

        result = start_mailing(mailing)

        self.assertIsNone(result)

        mock_send_mail.assert_called_once_with(
            subject=mailing.message.title,
            message=mailing.message.content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            fail_silently=False,
            recipient_list=[self.recipient1.email],
        )

        attempts = MailingAttempt.objects.filter(mailing=mailing)

        self.assertEqual(attempts.count(), 1)

        attempt = attempts.first()

        self.assertEqual(attempt.status, "success")
        self.assertTrue(attempt.run_id)
        self.assertIn(
            self.recipient1.email,
            attempt.server_response,
        )

    @patch("mailing_service.services.send_mail")
    def test_start_mailing_outside_time(self, mock_send_mail):
        """Отправка запрещена, если текущее время вне диапазона рассылки."""

        mailing = self.mailing1
        mailing.recipients.add(self.recipient1)

        # Рассылка уже закончилась.
        mailing.start_time = timezone.now() - timedelta(hours=2)
        mailing.end_time = timezone.now() - timedelta(hours=1)
        mailing.save()

        result = start_mailing(mailing)

        self.assertEqual(
            result,
            "Отправка запрещена по времени.",
        )

        # Письмо вообще не должно отправляться.
        mock_send_mail.assert_not_called()

        attempts = MailingAttempt.objects.filter(mailing=mailing)

        self.assertEqual(attempts.count(), 1)

        attempt = attempts.first()

        self.assertEqual(attempt.status, "failure")
        self.assertTrue(attempt.run_id)
        self.assertEqual(
            attempt.server_response,
            "Ошибка: Время не соответствует активности рассылки.",
        )

    def test_get_cache_loads_users_from_database(self):
        """При отсутствии кэша пользователи загружаются из БД."""

        users = get_cache()

        self.assertEqual(
            set(users),
            set(User.objects.filter(is_active=True)),
        )

        self.assertIsNotNone(cache.get("active_users_list"))

    def test_get_cache_returns_users_from_cache(self):
        """При наличии кэша пользователи берутся из кэша."""

        cached_users = [self.user1, self.user2]

        cache.set(
            "active_users_list",
            cached_users,
            300,
        )

        with patch("mailing_service.services.User.objects.filter") as mock_filter:
            result = get_cache()

        self.assertEqual(result, cached_users)
        mock_filter.assert_not_called()
