from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from mailing_service.models import Mailing, Recipient
from users.models import User


class Command(BaseCommand):
    help = "Создает группу 'Менеджеры' и назначает ей базовые права доступа"

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="Менеджеры")

        if created:
            self.stdout.write(self.style.SUCCESS("Группа 'Менеджеры' успешно создана!"))
        else:
            self.stdout.write(self.style.WARNING("Группа 'Менеджеры' уже существует!"))

        mailing = ContentType.objects.get_for_model(Mailing)
        recipient = ContentType.objects.get_for_model(Recipient)
        users = ContentType.objects.get_for_model(User)

        permissions = Permission.objects.filter(
            codename__in=[
                "view_mailing",
                "view_recipient",
                "view_user",
                "can_disable_distribution",
            ],
            content_type__in=[mailing, recipient, users],
        )

        group.permissions.set(permissions)

        self.stdout.write(self.style.SUCCESS(f"Группе успешно назначено прав: {permissions.count()} шт."))
