from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from mailing_service.tests.base_setup import BaseDataTest


class SendMailTest(BaseDataTest):
    """Тест начала рассылки."""

    def setUp(self):
        """Очистка кэша перед тестированием."""

        cache.clear()

    @patch("mailing_service.views.start_mailing")
    def test_user_can_start_own_mailing(self, mock_start_mailing):
        """Пользователь может запустить свою рассылку."""

        mock_start_mailing.return_value = None

        self.client.force_login(self.user1)

        response = self.client.post(
            reverse(
                "mailing_service:send_start",
                kwargs={"pk": self.mailing1.pk},
            )
        )

        self.assertRedirects(
            response,
            reverse("mailing_service:mailings_list"),
        )

        mock_start_mailing.assert_called_once_with(self.mailing1)

    @patch("mailing_service.views.start_mailing")
    def test_user_cannot_start_other_user_mailing(self, mock_start_mailing):
        """Пользователь не может запустить чужую рассылку."""

        self.client.force_login(self.user1)

        response = self.client.post(
            reverse(
                "mailing_service:send_start",
                kwargs={"pk": self.mailing2.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

        mock_start_mailing.assert_not_called()

    @patch("mailing_service.views.start_mailing")
    def test_manager_cannot_start_other_user_mailing(self, mock_start_mailing):
        """Менеджер не может запускать чужие рассылки."""

        self.client.force_login(self.manager)

        response = self.client.post(
            reverse(
                "mailing_service:send_start",
                kwargs={"pk": self.mailing1.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

        mock_start_mailing.assert_not_called()

    @patch("mailing_service.views.start_mailing")
    def test_superuser_can_start_any_mailing(self, mock_start_mailing):
        """Суперпользователь может запустить любую рассылку."""

        mock_start_mailing.return_value = None

        self.client.force_login(self.admin)

        response = self.client.post(
            reverse(
                "mailing_service:send_start",
                kwargs={"pk": self.mailing2.pk},
            )
        )

        self.assertRedirects(
            response,
            reverse("mailing_service:mailings_list"),
        )

        mock_start_mailing.assert_called_once_with(self.mailing2)
