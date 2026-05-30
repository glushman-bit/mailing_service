from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from mailing_service.models import MailingAttempt


def start_mailing(mailing):
    recipients = mailing.recipients.all()
    list_emails = [recipient.email for recipient in recipients]

    now = timezone.now()

    if not (mailing.start_time <= now <= mailing.end_time):

        MailingAttempt.objects.create(
            mailing=mailing,
            status='failure',
            server_response='Ошибка: Время не соответствует активности рассылки.',
        )
        return "Отправка запрещена по времени."

    if not list_emails:
        # запись в лог
        MailingAttempt.objects.create(
            mailing=mailing,
            status='failure',
            server_response='Ошибка: Список получателей пуст.',
        )
        return "Список получателей пуст."

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
            status='success',
            server_response='Рассылка успешно отправлена получателям.'
        )

        return None

    except Exception as e:
        MailingAttempt.objects.create(
            mailing=mailing,
            status='failure',
            server_response=str(e),
        )
        return str(e)
