from django import forms
from django.forms import ModelForm

from mailing_service.models import Recipient



class StyleFormMixin:
    """ Класс миксин для изменения форм """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})


class RecipientForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Recipient
        exclude = ("created_at",)
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }


