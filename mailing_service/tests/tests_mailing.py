from datetime import timedelta

from django.utils import timezone

from .base_setup import BaseDataTest
from django.core.cache import cache
from django.urls import reverse

from ..models import Mailing


class MailingTest(BaseDataTest):
    """Тестирование сообщений."""

    def setUp(self):
        """Очистка кэша перед тестированием."""

        cache.clear()

    def test_user_sees_only_own_mailings(self):
        """Обычный пользователь видит только свои рассылки."""

        self.client.force_login(self.user1)

        response = self.client.get(
            reverse("mailing_service:mailings_list")
        )

        self.assertEqual(response.status_code, 200)

        mailings = response.context["page_object"]

        self.assertIn(self.mailing1, mailings)
        self.assertNotIn(self.mailing2, mailings)

    def test_manager_sees_all_mailings(self):
        """Менеджер видит рассылки всех пользователей."""

        self.client.force_login(self.manager)

        response = self.client.get(
            reverse("mailing_service:mailings_list")
        )

        self.assertEqual(response.status_code, 200)

        mailings = response.context["page_object"]

        self.assertIn(self.mailing1, mailings)
        self.assertIn(self.mailing2, mailings)

    def test_user_can_view_own_mailing(self):
        """Пользователь может просматривать свои рассылки."""

        self.client.force_login(self.user1)

        response = self.client.get(
            reverse(
                "mailing_service:mailing_detail",
                kwargs={"pk": self.mailing1.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Сообщение пользователя")

    def test_user_cannot_view_other_users_mailing(self):
        """Пользователь не может просматривать чужие рассылки."""

        self.client.force_login(self.user1)

        response = self.client.get(
            reverse(
                "mailing_service:mailing_detail",
                kwargs={"pk": self.mailing2.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_manager_can_view_any_mailing(self):
        """Менеджер может просматривать любые рассылки."""

        self.client.force_login(self.manager)

        response = self.client.get(
            reverse(
                "mailing_service:mailing_detail",
                kwargs={"pk": self.mailing2.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Сообщение другого пользователя")

    def test_user_can_create_mailing(self):
        """Тест: Создание рассылки пользователем."""

        self.client.force_login(self.user1)

        response = self.client.post(
            reverse("mailing_service:mailing_create"),
            {
                "start_time": timezone.now() + timedelta(hours=1),
                "end_time": timezone.now() + timedelta(hours=2),
                "message": self.message1.pk,
                "recipients": [self.recipient1.pk],
            },
        )

        self.assertEqual(response.status_code, 302)

        mailing = Mailing.objects.latest("id")

        self.assertEqual(mailing.owner, self.user1)
        self.assertEqual(mailing.message, self.message1)
        self.assertIn(
            self.recipient1,
            mailing.recipients.all(),
        )

    def test_create_form_contains_only_user_messages_and_recipients(self):
        """Тест фильтрации формы сообщений и получателей."""

        self.client.force_login(self.user1)

        response = self.client.get(
            reverse("mailing_service:mailing_create")
        )

        self.assertEqual(response.status_code, 200)

        form = response.context["form"]

        message_queryset = form.fields["message"].queryset
        recipient_queryset = form.fields["recipients"].queryset

        self.assertIn(self.message1, message_queryset,)
        self.assertNotIn(self.message2, message_queryset,)

        self.assertIn(self.recipient1, recipient_queryset,)
        self.assertNotIn(self.recipient2, recipient_queryset,)

    def test_user_cannot_create_mailing_with_other_user_data(self):
        """Пользователь не может создать рассылку с чужими данными."""

        self.client.force_login(self.user1)

        response = self.client.post(
            reverse("mailing_service:mailing_create"),
            {
                "start_time": timezone.now() + timedelta(hours=1),
                "end_time": timezone.now() + timedelta(hours=2),
                "message": self.message2.pk,
                "recipients": [self.recipient2.pk],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Mailing.objects.filter(owner=self.user1).count(),
            1,
        )
        self.assertFalse(
            Mailing.objects.filter(
                owner=self.user1, message=self.message2,
            ).exists()
        )


    def test_anonymous_user_cannot_create_mailing(self):
        """Анонимный пользователь не может создать рассылку."""

        response = self.client.get(
            reverse("mailing_service:mailing_create"),
            follow=False,
        )

        self.assertEqual(response.status_code, 302)

    def test_user_can_update_own_mailing(self):
        """Пользователь может редактировать свою рассылку."""

        self.client.force_login(self.user1)

        response = self.client.post(
            reverse(
                "mailing_service:mailing_update",
                kwargs={"pk": self.mailing1.pk},
            ),
            {
                "start_time": timezone.now() + timedelta(hours=3),
                "end_time": timezone.now() + timedelta(hours=4),
                "message": self.message1.pk,
                "recipients": [self.recipient1.pk],
            },
        )

        self.assertRedirects(response, reverse("mailing_service:mailings_list"))

        self.mailing1.refresh_from_db()

        self.assertEqual(self.mailing1.message, self.message1,)

    def test_user_cannot_update_other_user_mailing(self):
        """Пользователь не может редактировать чужую рассылку."""

        self.client.force_login(self.user1)

        response = self.client.post(
            reverse(
                "mailing_service:mailing_update",
                kwargs={"pk": self.mailing2.pk},
            ),
            {
                "start_time": timezone.now() + timedelta(hours=3),
                "end_time": timezone.now() + timedelta(hours=4),
                "message": self.message1.pk,
                "recipients": [self.recipient1.pk],
            },
        )

        self.assertEqual(response.status_code, 404)

        self.mailing2.refresh_from_db()

        self.assertEqual(self.mailing2.message, self.message2)

    def test_user_can_delete_own_mailing(self):
        """Пользователь может удалить свою рассылку."""

        self.client.force_login(self.user1)

        mailing_id = self.mailing1.pk

        response = self.client.post(
            reverse(
                "mailing_service:mailing_delete",
                kwargs={"pk": mailing_id},
            )
        )

        self.assertRedirects(response, reverse("mailing_service:mailings_list"))

        self.assertFalse(Mailing.objects.filter(pk=mailing_id).exists())
