from .base_setup import BaseDataTest
from django.core.cache import cache
from django.urls import reverse

from ..models import Message


class MessageTest(BaseDataTest):
    """Тестирование сообщений."""

    def setUp(self):
        """Очистка кэша перед тестированием."""

        cache.clear()

    def test_user_sees_only_own_messages(self):
        """Обычный пользователь видит только свои сообщения."""

        self.client.force_login(self.user1)

        response = self.client.get(
            reverse("mailing_service:messages_list")
        )

        self.assertEqual(response.status_code, 200)

        messages = response.context["page_object"]

        self.assertIn(self.message1, messages)
        self.assertNotIn(self.message2, messages)

    def test_manager_sees_all_messages(self):
        """Менеджер видит сообщения всех пользователей."""

        self.client.force_login(self.manager)

        response = self.client.get(
            reverse("mailing_service:messages_list")
        )

        self.assertEqual(response.status_code, 200)

        messages = response.context["page_object"]

        self.assertIn(self.message1, messages)
        self.assertIn(self.message2, messages)

    def test_user_can_view_own_not_other_message(self):
        """Пользователь может просматривать своё сообщение."""

        self.client.force_login(self.user1)

        response_own = self.client.get(
            reverse(
                "mailing_service:message_detail",
                args=[self.message1.pk],
            )
        )
        response_other = self.client.get(
            reverse(
                "mailing_service:message_detail",
                args=[self.message2.pk],
            )
        )

        self.assertEqual(response_own.status_code, 200)
        self.assertEqual(response_other.status_code, 404)

    def test_manager_can_view_foreign_message(self):
        """Менеджер может просматривать сообщения пользователей."""

        self.client.force_login(self.manager)

        response = self.client.get(
            reverse(
                "mailing_service:message_detail",
                args=[self.message1.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_user_can_edit_own_cannot_other_message(self):
        """Пользователь может редактировать свои сообщения."""

        self.client.force_login(self.user1)

        response_upd_own = self.client.get(
            reverse(
                "mailing_service:message_update",
                args=[self.message1.pk],
            )
        )
        response_upd_other = self.client.get(
            reverse(
                "mailing_service:message_update",
                args=[self.message2.pk],
            )
        )

        self.assertEqual(response_upd_own.status_code, 200)
        self.assertEqual(response_upd_other.status_code, 404)

    def test_manager_cannot_edit_foreign_message(self):
        """Менеджер не может редактировать чужое сообщение."""

        self.client.force_login(self.manager)

        response = self.client.get(
            reverse(
                "mailing_service:message_update",
                args=[self.message1.pk],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_user_can_delete_own_cannot_foreign_message(self):
        """Пользователь может открыть страницу удаления своего сообщения."""

        self.client.force_login(self.user1)

        response_del_own = self.client.get(
            reverse(
                "mailing_service:message_delete",
                args=[self.message1.pk],
            )
        )
        response_del_other = self.client.get(
            reverse(
                "mailing_service:message_delete",
                args=[self.message2.pk],
            )
        )

        self.assertEqual(response_del_own.status_code, 200)
        self.assertEqual(response_del_other.status_code, 404)

    def test_user_can_create_message(self):
        """Пользователь может создать сообщение."""

        self.client.force_login(self.user1)

        response = self.client.post(
            reverse("mailing_service:message_create"),
            {
                "title": "Новое тестовое сообщение",
                "content": "Текст нового тестового сообщения",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.message = Message.objects.get(title="Новое тестовое сообщение")

        self.assertEqual(self.message.owner, self.user1)

    def test_created_message_belongs_to_current_user(self):
        """Созданное сообщение принадлежит текущему пользователю."""

        self.client.force_login(self.user2)

        response = self.client.post(
            reverse("mailing_service:message_create"),
            {
                "title": "Сообщение тест другого пользователя",
                "content": "Текст сообщения",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.message = Message.objects.get(title="Сообщение тест другого пользователя")

        self.assertEqual(self.message.owner, self.user2)
        self.assertNotEqual(self.message.owner, self.user1)

    def test_anonymous_user_cannot_create_message(self):
        """Неавторизованный пользователь не может создать сообщение."""

        response = self.client.get(
            reverse("mailing_service:message_create")
        )

        self.assertEqual(response.status_code, 302)
