from .base_setup import BaseDataTest
from django.core.cache import cache
from django.urls import reverse


class RecipientTest(BaseDataTest):
    """Тестирование получателей рассылок."""

    def setUp(self):
        """Очистка кэша перед тестированием."""

        cache.clear()

    def test_user_sees_only_own_recipients(self):
        """Тест: пользователь видит только своих получателей."""

        self.client.force_login(self.user1)

        response = self.client.get(
            reverse("mailing_service:recipients_list")
        )

        self.assertEqual(response.status_code, 200)

        recipients = response.context["page_object"]

        self.assertIn(self.recipient1, recipients)
        self.assertNotIn(self.recipient2, recipients)


    def test_user_can_update_delete_own_recipients(self):
        """Тест: пользователь может изменять и удалять своих получателей."""

        self.client.force_login(self.user1)
        response = self.client.post(
            reverse(
                "mailing_service:recipient_update",
                kwargs={"pk": self.recipient1.id}
            ),{
                "email": "updated@test.com",
                "full_name": "Пётр Петров",
                "comment": "Новый комментарий",
            }
        )
        response_del = self.client.get(
            reverse(
                "mailing_service:recipient_delete",
                args=[self.recipient1.id]
            )
        )

        self.assertRedirects(response, reverse("mailing_service:recipients_list"))

        self.recipient1.refresh_from_db()

        self.assertEqual(self.recipient1.full_name, "Пётр Петров")
        self.assertEqual(self.recipient1.comment, "Новый комментарий")

        self.assertEqual(response_del.status_code, 200)

    def test_user_cannot_update_delete_another_recipients(self):
        """Тест: пользователь не может изменять чужого получателя."""

        self.client.force_login(self.user1)
        response = self.client.post(
            reverse(
                "mailing_service:recipient_update",
                kwargs={"pk": self.recipient2.id}
            ),{
                "email": "hacked@test.com",
                "full_name": "Изменён",
                "comment": "Изменено",
            }
        )

        self.assertEqual(response.status_code, 404)

        self.recipient2.refresh_from_db()

        self.assertEqual(self.recipient2.email, "recipient2@test.com")
        self.assertEqual(self.recipient2.full_name, "User Two")
        self.assertEqual(self.recipient2.comment, "Test")

    def test_manager_sees_all_recipients(self):
        """Тест: менеджер видит всех получателей."""

        self.user1.is_staff = True
        self.user1.save(update_fields=["is_staff"])

        self.client.force_login(self.user1)
        response = self.client.get(
            reverse("mailing_service:recipients_list")
        )

        self.assertEqual(response.status_code, 200)

        recipients = response.context["page_object"]

        self.assertIn(self.recipient1, recipients)
        self.assertIn(self.recipient2, recipients)

    def test_manager_cannot_edit_delete_foreign_recipient(self):
        """Менеджер не может редактировать чужого получателя."""

        self.client.force_login(self.manager)

        response_upd = self.client.get(
            reverse(
                "mailing_service:recipient_update",
                args=[self.recipient1.pk],
            )
        )
        response_del = self.client.get(
            reverse(
                "mailing_service:recipient_delete",
                args=[self.recipient1.pk]
            )
        )

        self.assertEqual(response_upd.status_code, 404)
        self.assertEqual(response_del.status_code, 404)
