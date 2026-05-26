from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from mailing_service.models import Recipient, Message, Mailing
from mailing_service.forms import RecipientForm, MessageForm, MailingForm


class MainPageView(TemplateView):
    """ Класс вывода главной страницы """
    template_name = "mailing_service/main_page.html"

    def get_context_data(self, **kwargs):
        """ Добавление данных на главную страницу """
        context = super().get_context_data(**kwargs)

        recipients = Recipient.objects.all()
        context["recipients_all"] = len(list(recipient for recipient in recipients))
        messages = Message.objects.all()
        context["messages_all"] = len(list(message for message in messages))
        mailings = Mailing.objects.all()
        context["mailings_all"] = len(list(mailing for mailing in mailings))

        return context


class RecipientListView(ListView):
    """ Класс представления списка получателей рассылки """
    model = Recipient
    template_name = "mailing_service/recipients_list.html"
    context_object_name = "page_object"
    paginate_by = 10
    ordering = ["created_at"]


class RecipientDetailView(DetailView):
    """ Класс представления детальной информации о получателе рассылки """
    model = Recipient
    template_name = "mailing_service/recipient_detail.html"
    context_object_name = "recipient"
    success_url = reverse_lazy("mailing_service:recipients_list")


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:recipients_list")
    extra_context = {
        "back_url": "mailing_service:recipients_list",
        "object_type": "Recipient",
    }



class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:recipients_list")
    extra_context = {
        "back_url": "mailing_service:recipients_list",
        "object_type": "Recipient",
    }


class RecipientDeleteView(DeleteView):
    model = Recipient
    template_name = "mailing_service/confirm_delete.html"
    success_url = reverse_lazy("mailing_service:recipients_list")
    extra_context = {
        "back_url": "mailing_service:recipients_list",
        "object_type": "Recipient",
    }


class MessageListView(ListView):
    model = Message
    template_name = "mailing_service/messages_list.html"
    context_object_name = "page_object"
    paginate_by = 10
    ordering = ["created_at"]


class MessageDetailView(DetailView):
    model = Message
    template_name = "mailing_service/message_detail.html"
    context_object_name = "message"
    success_url = reverse_lazy("mailing_service:messages_list")


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:messages_list")
    extra_context = {
        "back_url": "mailing_service:messages_list",
        "object_type": "Message",
    }


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:messages_list")
    extra_context = {
        "back_url": "mailing_service:messages_list",
        "object_type": "Message",
    }


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "mailing_service/confirm_delete.html"
    success_url = reverse_lazy("mailing_service:messages_list")
    extra_context = {
        "back_url": "mailing_service:messages_list",
        "object_type": "Message",
    }


class MailingListView(ListView):
    model = Mailing
    template_name = "mailing_service/mailings_list.html"
    context_object_name = "page_object"
    paginate_by = 10
    ordering = ["created_at"]


class MailingDetailView(DetailView):
    model = Mailing
    template_name = "mailing_service/mailing_detail.html"
    context_object_name = "mailing"
    success_url = reverse_lazy("mailing_service:mailings_list")


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:mailings_list")
    extra_context = {
        "back_url": "mailing_service:mailings_list",
        "object_type": "Mailing",
    }


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:mailings_list")
    extra_context = {
        "back_url": "mailing_service:mailings_list",
        "object_type": "Mailing",
    }


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = "mailing_service/confirm_delete.html"
    success_url = reverse_lazy("mailing_service:mailings_list")
    extra_context = {
        "back_url": "mailing_service:mailings_list",
        "object_type": "Mailing",
    }
