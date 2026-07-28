from django import forms
from django.forms import ModelForm

from mailing_service.models import Mailing, Message, Recipient


class StyleFormMixin:
    """Класс миксин для изменения форм"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})


class RecipientForm(StyleFormMixin, ModelForm):
    """Класс формы для получателей рассылки"""

    class Meta:
        model = Recipient
        exclude = (
            "created_at",
            "owner",
        )
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }


class MessageForm(StyleFormMixin, ModelForm):
    """Класс формы для сообщений"""

    class Meta:
        model = Message
        exclude = (
            "created_at",
            "owner",
        )
        widgets = {
            "content": forms.Textarea(attrs={"row": 3}),
        }


class MailingForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Mailing
        fields = ["start_time", "end_time", "message", "recipients"]
        widgets = {
            "start_time": forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
            ),
            "end_time": forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={
                    "class": "form-control",
                    'type': 'datetime-local',
                },
            ),
        }
