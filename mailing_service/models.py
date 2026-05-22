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
        help_text="Введите Имя, Фамилию и Отчество",
    )
    comment = models.TextField(
        verbose_name="Комментарий",
        help_text="Введите комментарий",
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

    class Meta:
        verbose_name = "Письмо"
        verbose_name_plural = "Письма"

    def __str__(self):
        return self.title


class Mailing(models.Model):
    """ Класс рассылки """

    STATUS_CREATED = 'created'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'

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
        max_length=10,
        choices=CHOICES_STATUS,
        default=STATUS_CREATED,
        verbose_name="Статус",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="Сообщение",
    )
    recipients = models.ManyToManyField(
        Recipient,
        related_name="Сообщения",
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
