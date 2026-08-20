from django.contrib.auth.models import Group
from django.test import TestCase

from users.models import User


class UserTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(email='Test_1@example.com')
        self.user1.set_password('test1234')
        self.user1.save()

        self.user2 = User.objects.create(email='Test_2@example.com')
        self.user2.set_password('test1234')
        self.user2.save()

        self.manager = User.objects.create(email='manager@example.com')
        self.manager.set_password('test1234')
        self.manager.is_staff = True
        self.manager.save()

        managers_group = Group.objects.create(name='Менеджеры')
        self.manager.groups.add(managers_group)

        self.admin = User.objects.create(email='admin@example.com')
        self.admin.set_password('test1234')
        self.admin.is_superuser = True
        self.admin.is_staff = True
        self.admin.save()
