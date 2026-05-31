from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone, cache
from mailing_service.models import MailingAttempt


def start_mailing(mailing):
    """ Функция отправки сообщений получателям рассылок.
        Логирования данных в Admin.
        Отправки лог данных в БД"""
    recipients = mailing.recipients.all()
    list_emails = [recipient.email for recipient in recipients]

    now = timezone.now()
    attempts_batch = []

    if not (mailing.start_time <= now <= mailing.end_time):
        # запись в лог
        MailingAttempt.objects.create(
            mailing=mailing,
            status='failure',
            server_response='Ошибка: Время не соответствует активности рассылки.',
        )
        return 'Отправка запрещена по времени.'

    if not list_emails:
        # запись в лог
        MailingAttempt.objects.create(
            mailing=mailing,
            status='failure',
            server_response='Ошибка: Список получателей пуст.',
        )
        return "Список получателей пуст."

    status = 'success'
    response_text = f'Письма успешно отправлены на {len(list_emails)} адрес(ов).'

    try:
        send_mail(
            subject=mailing.message.title,
            message=mailing.message.content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            fail_silently=False,
            recipient_list=list_emails,
        )
        # запись в лог
        MailingAttempt.objects.create(
            mailing=mailing,
            status=status,
            server_response=response_text
        )
    except Exception as e:
        status = 'failure'
        response_text = f'Сбой отправки: {str(e)}'

        new_attempt = MailingAttempt(
            mailing=mailing,
            status=status,
            server_response=response_text,
        )
        attempts_batch.append(new_attempt)

        if attempts_batch:
            MailingAttempt.objects.bulk_create(attempts_batch, batch_size=100)

        return response_text


def get_cache():
    """ Функция кэширования данных """
    users = cache.get('active_users_list')

    if not users:
        users = list(User.objects.filter(is_active=True))
        cache.set('active_users_list', users, 300)

    return users
