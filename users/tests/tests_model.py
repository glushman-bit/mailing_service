from users.models import User

from .base_setup import UserTest


class UserModelTest(UserTest):
    """Тесты для models.py"""

    def test_user_create(self):
        """Проверяем создание пользователя."""

        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(self.user1.email, 'Test_1@example.com')

    def test_email_is_username(self):
        """Email используется как идентификатор пользователя."""

        self.assertEqual(self.user1.USERNAME_FIELD, 'email')

    def test_str_returns_email(self):
        """__str__() возвращает email пользователя."""

        self.assertEqual(str(self.user1), 'Test_1@example.com')

    def test_password_is_hash(self):
        """Пароль не хранится в БД в открытом виде."""

        self.assertNotEqual(self.user1.password, 'test1234')
        self.assertTrue(self.user1.check_password('test1234'))

    def test_default_avatar_url(self):
        """Без аватара используется стандартный аватар."""

        self.assertIn("avatar/default-avatar.jpg", self.user1.get_avatar_url)
