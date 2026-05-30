from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Recipient(models.Model):
    """ Класс получателя рассылки """
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Введите Email",
    )
    full_name = models.CharField(
        max_length=100,
        verbose_name="Ф.И.О.",
        help_text="Введите Фамилию, Имя и Отчество",
    )
    comment = models.TextField(
        verbose_name="Комментарий",
        help_text="Введите комментарий",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылок"

    def __str__(self):
        return self.email


class Message(models.Model):
    """ Класс сообщения """
    title = models.CharField(
        max_length=100,
        verbose_name="Тема письма",
        help_text="Введите тему письма",
    )
    content = models.TextField(
        verbose_name="Сообщение",
        help_text="Введите сообщение"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Письмо"
        verbose_name_plural = "Письма"

    def __str__(self):
        return self.title


class Mailing(models.Model):
    """ Класс рассылки """

    STATUS_CREATED = 'Создана'
    STATUS_RUNNING = 'Запущена'
    STATUS_COMPLETED = 'Завершена'

    CHOICES_STATUS = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_RUNNING, 'Запущена'),
        (STATUS_COMPLETED, 'Завершена'),
    ]

    start_time = models.DateTimeField(
        verbose_name="Начало рассылки",
        help_text="Введите дату и время начало рассылки",
    )
    end_time = models.DateTimeField(
        verbose_name="Конец рассылки",
        help_text="Введите дату и время окончания рассылки",
    )
    status = models.CharField(
        max_length=20,
        choices=CHOICES_STATUS,
        default=STATUS_CREATED,
        verbose_name="Статус",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Сообщение",
    )
    recipients = models.ManyToManyField(
        Recipient,
        blank=True,
        related_name="mailings",
        verbose_name="Получатели рассылки",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return self.message.title

    def update_status(self):
        """ Обновление статуса рассылки по текущему времени """
        now = timezone.now()

        if now < self.start_time:
            new_status = self.STATUS_CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.STATUS_RUNNING
        else:
            new_status = self.STATUS_COMPLETED

        if new_status != self.status:
            self.status = new_status
            self.save(update_fields=["status"])

    def clean(self):
        """ Валидация даты начала рассылки """
        if self.start_time >= self.end_time:
            raise ValidationError("Дата окончания не может быть раньше даты начала")


class MailingAttempt(models.Model):
    """ Класс попытки рассылки """
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failure', 'Не успешно'),
    ]
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        verbose_name="Рассылка",
        related_name="attempts",
    )
    attempt_time  = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время попытки рассылки",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name="Статус попытки",
    )
    server_response = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ответ почтового сервера",
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        ordering = ['-attempt_time']

    def __str__(self):
        return f"Попытка для рассылки #{self.mailing_id} от {self.attempt_time.strftime('%d.%m.%Y %H:%M')}"
