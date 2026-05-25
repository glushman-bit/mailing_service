from enum import unique

from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from mailing_service.models import Recipient, Message, Mailing


class MainPageView(TemplateView):
    """ Класс вывода главной страницы """
    template_name = "mailing_service/main_page.html"

    def get_context_data(self, **kwargs):
        """ Добавление данных на главную страницу """
        context = super().get_context_data(**kwargs)

        print(context)

        recipients = Recipient.objects.all()
        context["recipients_all"] = len(list(recipient for recipient in recipients))
        messages = Message.objects.all()
        context["messages_all"] = len(list(message for message in messages))
        mailings = Mailing.objects.all()
        context["mailings_all"] = len(list(mailing for mailing in mailings))

        return context


class RecipientListView(ListView):
    model = Recipient
    template_name = "mailing_service/recipients_list.html"
    context_object_name = "page_object"
    paginate_by = 10
    ordering = ["created_at"]


class MessageListView(ListView):
    model = Message
    template_name = "mailing_service/messages_list.html"
    context_object_name = "page_object"
    paginate_by = 10
    ordering = ["created_at"]


class MailingListView(ListView):
    model = Mailing
    template_name = "mailing_service/mailings_list.html"
    context_object_name = "page_object"
    paginate_by = 10
    ordering = ["created_at"]

