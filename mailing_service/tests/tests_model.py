from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from mailing_service.models import Mailing
from mailing_service.tests.base_setup import BaseDataTest


class ModelTest(BaseDataTest):
    """Класс тестирования модели."""

    def test_status_is_created_if_mailing_has_not_started(self):
        """Тест статуса рассылки - "создана"."""

        self.client.force_login(self.user1)

        self.mailing1.start_time = timezone.now() + timedelta(hours=1)
        self.mailing1.end_time = timezone.now() + timedelta(hours=2)
        self.mailing1.status = Mailing.STATUS_CREATED
        self.mailing1.save()

        self.client.get(
            reverse(
                "mailing_service:mailing_detail",
                kwargs={"pk": self.mailing1.pk},
            )
        )

        self.mailing1.refresh_from_db()

        self.assertEqual(
            self.mailing1.status,
            Mailing.STATUS_CREATED,
        )

    def test_status_is_running_during_mailing(self):
        """Тест статуса рассылки - "запущена"."""

        self.client.force_login(self.user1)

        self.mailing1.start_time = timezone.now() - timedelta(hours=1)
        self.mailing1.end_time = timezone.now() + timedelta(hours=1)
        self.mailing1.status = Mailing.STATUS_RUNNING
        self.mailing1.save()

        self.client.get(
            reverse(
                "mailing_service:mailing_detail",
                kwargs={"pk": self.mailing1.pk},
            )
        )

        self.mailing1.refresh_from_db()

        self.assertEqual(
            self.mailing1.status,
            Mailing.STATUS_RUNNING,
        )

    def test_status_is_completed_after_mailing(self):
        """Тест статуса рассылки - "завершена"."""

        self.client.force_login(self.user1)

        self.mailing1.start_time = timezone.now() - timedelta(hours=2)
        self.mailing1.end_time = timezone.now() - timedelta(hours=1)
        self.mailing1.status = Mailing.STATUS_RUNNING
        self.mailing1.save()

        self.client.get(
            reverse(
                "mailing_service:mailing_detail",
                kwargs={"pk": self.mailing1.pk},
            )
        )

        self.mailing1.refresh_from_db()

        self.assertEqual(
            self.mailing1.status,
            Mailing.STATUS_COMPLETED,
        )
