import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone


from mailing_service.models import MailingAttempt
from users.models import User


def start_mailing(mailing):
    """Функция отправки сообщений получателям по отдельности.
    Логирование КАЖДОЙ попытки отправки через пакетный метод batch (bulk_create)"""
    recipients = mailing.recipients.all()
    now = timezone.now()

    attempts_batch = []
    failed_emails = []
    # Генерируем уникальный маркер "этого конкретного запуска" для всей пачки писем
    current_run_id = str(uuid.uuid4())

    if not (mailing.start_time <= now <= mailing.end_time):
        MailingAttempt.objects.create(
            mailing=mailing,
            status='failure',
            run_id=current_run_id,
            server_response='Ошибка: Время не соответствует активности рассылки.',
        )
        return 'Отправка запрещена по времени.'

    if not recipients.exists():
        MailingAttempt.objects.create(
            mailing=mailing,
            status='failure',
            run_id=current_run_id,
            server_response='Ошибка: Список получателей пуст.',
        )
        return "Список получателей пуст."

    # Цикл отправки писем по отдельности
    for recipient in recipients:
        try:
            send_mail(
                subject=mailing.message.title,
                message=mailing.message.content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                fail_silently=False,
                recipient_list=[recipient.email],
            )
            status = 'success'
            response_text = f'Письмо успешно отправлено на {recipient.email}.'
        except Exception as e:
            status = 'failure'
            response_text = f'Сбой отправки на {recipient.email}: {str(e)}'
            failed_emails.append(recipient.email)

        # Формируем объект лога для КАЖДОГО письма в памяти
        new_attempt = MailingAttempt(
            mailing=mailing,
            status=status,
            server_response=response_text,
            run_id=current_run_id,  # Привязываем к общему маркеру запуска
        )
        attempts_batch.append(new_attempt)

    # сохраняем все логи одним запросом к БД. (BATCH)
    if attempts_batch:
        MailingAttempt.objects.bulk_create(attempts_batch, batch_size=100)

    # Возвращаем информацию для всплывающего сообщения во View
    if failed_emails:
        return f"Не удалось отправить письма на: {', '.join(failed_emails)}"

    return None


def get_cache():
    """Функция кэширования данных"""
    users = cache.get('active_users_list')

    if not users:
        users = list(User.objects.filter(is_active=True))
        cache.set('active_users_list', users, 300)

    return users
