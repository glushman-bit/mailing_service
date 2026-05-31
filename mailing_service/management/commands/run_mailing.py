from apscheduler.triggers.cron import CronTrigger
from django.core.management import BaseCommand
from django.utils import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from django_apscheduler.jobstores import DjangoJobStore

from config import settings
from mailing_service.models import Mailing
from mailing_service.services import start_mailing
import logging


logger = logging.getLogger(__name__)


def run_mailing():
    """ Функция проверки какие рассылки необходимо отправлять """
    now = timezone.now()

    active_mailings = Mailing.objects.filter(
        start_time__lte=now,
        end_time__gte=now,
    ).exclude(status='Завершена')

    for mailing in active_mailings:
        logger.info(f"Запуск автоматической отправки рассылки ID {mailing.id}")
        start_mailing(mailing)


class Command(BaseCommand):
    help = 'Запуск планировщика задач APScheduler.'

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        scheduler.add_job(
            run_mailing,
            trigger=CronTrigger(second=0),
            id="run_mailing",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Планировщик успешно запущен...")

        try:
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Планировщик остановлен.")
            scheduler.shutdown()
