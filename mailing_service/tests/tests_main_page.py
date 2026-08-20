from django.urls import reverse

from mailing_service.tests.base_setup import BaseDataTest


class MainPageViewTest(BaseDataTest):
    """Тесты главной страницы."""

    def test_anonymous_user_sees_empty_statistics(self):
        """Неавторизованный пользователь получает нулевую статистику."""

        response = self.client.get(
            reverse("mailing_service:main_page")
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["recipients_all"], 0)
        self.assertEqual(response.context["messages_all"], 0)
        self.assertEqual(response.context["mailings_all"], 0)
        self.assertEqual(response.context["mailings_create"], 0)
        self.assertEqual(response.context["mailings_running"], 0)
        self.assertEqual(response.context["mailings_completed"], 0)
        self.assertEqual(response.context["messages_success"], 0)
        self.assertEqual(response.context["sent_mailings_success"], 0)
        self.assertEqual(response.context["sent_mailings_error"], 0)

    def test_user_sees_only_own_statistics(self):
        """Пользователь видит статистику только своих объектов."""

        self.client.force_login(self.user1)

        response = self.client.get(
            reverse("mailing_service:main_page")
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["recipients_all"], 1)
        self.assertEqual(response.context["messages_all"], 1)
        self.assertEqual(response.context["mailings_all"], 1)

        self.assertEqual(
            list(response.context["recipients_last"]),
            [self.recipient1],
        )

        self.assertEqual(
            list(response.context["messages_last"]),
            [self.message1],
        )

    def test_manager_sees_all_statistics(self):
        """Менеджер видит статистику по всем объектам."""

        self.client.force_login(self.manager)

        response = self.client.get(
            reverse("mailing_service:main_page")
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["recipients_all"], 2)
        self.assertEqual(response.context["messages_all"], 2)
        self.assertEqual(response.context["mailings_all"], 2)

        self.assertEqual(response.context["mailings_create"], 2)
        self.assertEqual(response.context["mailings_running"], 0)
        self.assertEqual(response.context["mailings_completed"], 0)