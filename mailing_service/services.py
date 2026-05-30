from django.core.mail import send_mail

from django.conf import settings


def start_mailing(mailing):
    recipients = mailing.recipients.all()
    list_emails = [recipient.email for recipient in recipients]

    if not list_emails:
        raise ValueError("Список получателей пуст.")

    try:
        send_mail(
            subject=mailing.message.title,
            message=mailing.message.content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            fail_silently=False,
            recipient_list=list_emails,
        )
    except Exception as e:
        print(f"Ошибка: {e}")
