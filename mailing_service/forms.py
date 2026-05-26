from django import forms
from django.forms import ModelForm

from mailing_service.models import Recipient, Message


class StyleFormMixin:
    """ Класс миксин для изменения форм """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})


class RecipientForm(StyleFormMixin, ModelForm):
    """ Класс формы для получателей рассылки """
    class Meta:
        model = Recipient
        exclude = ("created_at",)
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }


class MessageForm(StyleFormMixin, ModelForm):
    """ Класс формы для сообщений """
    class Meta:
        model = Message
        exclude = ("created_at",)
        widgets = {
            "content": forms.Textarea(attrs={"row": 3}),
        }