from django.core import mail
from django.urls import reverse

from users.models import User
from users.tests.base_setup import UserTest


class UserViewsTests(UserTest):
    """Тесты для views.py"""

    def test_superuser_can_open_users_list(self):
        """Тест: открытие списка пользователей суперпользователем."""

        self.client.force_login(self.admin)
        response = self.client.get(reverse('users:users_list'))

        self.assertEqual(response.status_code, 200)

    def test_manager_can_open_users_list(self):
        """Тест: открытие списка пользователей персоналом."""

        self.client.force_login(self.manager)
        response = self.client.get(reverse('users:users_list'))

        self.assertEqual(response.status_code, 200)

    def test_user_can_open_users_list(self):
        """Тест: не открытие списка пользователей обычным пользователем."""

        self.client.force_login(self.user1)
        response = self.client.get(reverse('users:users_list'))

        self.assertEqual(response.status_code, 403)

    def test_not_login_can_open_users_list(self):
        """Тест: не открытие списка пользователей неавторизованным пользователем."""

        self.client.aforce_login(self.user1)
        response = self.client.get(reverse('users:users_list'))

        self.assertEqual(response.status_code, 302)

    def test_user_sees_own_profile_and_cannot_another(self):
        """Тест: пользователь может просмотреть свой профиль
        и не может чужой."""

        self.client.force_login(self.user1)
        response = self.client.get(reverse('users:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], self.user1)
        self.assertNotEqual(response.context['profile'], self.user2)

    def test_user_update_own_profile(self):
        """Тест: пользователь может изменить свой профиль."""

        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('users:profile_update'),
            {
                "email": "new@test.ru",
                "phone_number": "+79991234567",
                "country": "RU",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, "new@test.ru")
        self.assertEqual(self.user1.phone_number.as_e164, "+79991234567")

    def test_manager_can_block_user(self):
        """Тест: персонал может заблокировать пользователя."""

        self.client.force_login(self.manager)
        response = self.client.post(reverse("users:toggle_user_active", kwargs={"pk": self.user1.pk}))

        self.assertEqual(response.status_code, 302)

        self.user1.refresh_from_db()

        self.assertFalse(self.user1.is_active)

    def test_manager_can_unblock_user(self):
        """Тест: персонал может разблокировать пользователя."""

        self.user2.is_active = False
        self.user2.save()

        self.client.force_login(self.manager)
        response = self.client.post(reverse("users:toggle_user_active", kwargs={"pk": self.user2.pk}))

        self.assertEqual(response.status_code, 302)

        self.user2.refresh_from_db()

        self.assertTrue(self.user2.is_active)

    def test_manager_cannot_block_himself(self):
        """Тест: нельзя заблокировать самого себя."""

        self.client.force_login(self.manager)
        response = self.client.post(
            reverse(
                "users:toggle_user_active",
                kwargs={"pk": self.manager.pk},
            )
        )

        self.assertEqual(first=response.status_code, second=302)

        self.manager.refresh_from_db()

        self.assertTrue(self.manager.is_active)

    def test_manager_cannot_block_superuser(self):
        """Тест: нельзя заблокировать суперпользователя."""

        self.client.force_login(self.manager)
        response = self.client.post(
            reverse(
                "users:toggle_user_active",
                kwargs={"pk": self.admin.pk},
            )
        )

        self.assertEqual(response.status_code, 302)

        self.admin.refresh_from_db()

        self.assertTrue(self.admin.is_active)

    def test_regular_user_cannot_toggle_user(self):
        """Тест: обычный пользователь не может заблокировать другого пользователя."""

        self.client.force_login(self.user1)
        response = self.client.post(
            reverse(
                "users:toggle_user_active",
                kwargs={"pk": self.user2.pk},
            )
        )

        self.assertEqual(response.status_code, 403)

        self.user2.refresh_from_db()

        self.assertTrue(self.user2.is_active)

    def test_user_create_sends_confirmation_email(self):
        """Тест: при регистрации создаётся неактивный пользователь
        и отправляется письмо с подтверждением."""

        response = self.client.post(
            reverse("users:register"),
            {
                "email": "newuser@example.com",
                "phone_number": "+79991234567",
                "password1": "TestPassword123!",
                "password2": "TestPassword123!",
            },
        )

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(email="newuser@example.com")

        self.assertFalse(user.is_active)
        self.assertIsNotNone(user.token)

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(email.subject, "Подтверждение почты")
        self.assertEqual(email.to, ["newuser@example.com"])
        self.assertIn(user.token, email.body)

    def test_email_verification_activates_user(self):
        """Тест: подтверждение почты активирует пользователя."""

        user = User.objects.create(
            email="inactive@example.com",
            is_active=False,
            token="test-confirmation-token",
        )

        response = self.client.get(
            reverse(
                "users:email_confirm",
                kwargs={"token": user.token},
            )
        )

        user.refresh_from_db()

        self.assertTrue(user.is_active)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_email_verification_invalid_token(self):
        """Тест: подтверждение с неверным токеном возвращает 404."""

        response = self.client.get(
            reverse(
                "users:email_confirm",
                kwargs={"token": "invalid-token"},
            )
        )

        self.assertEqual(response.status_code, 404)
