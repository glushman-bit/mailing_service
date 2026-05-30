from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views import View
from django.db.models import Q

from mailing_service.models import Recipient, Message, Mailing, MailingAttempt
from mailing_service.forms import RecipientForm, MessageForm, MailingForm
from mailing_service.services import start_mailing


class MainPageView(TemplateView):
    """ Класс вывода главной страницы """
    template_name = "mailing_service/main_page.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Mailing.objects.filter(owner=self.request.user)
        return Mailing.objects.none()

    def get_context_data(self, **kwargs):
        """ Добавление данных на главную страницу """
        context = super().get_context_data(**kwargs)

        recipients = Recipient.objects.all()
        context["recipients_all"] = len([recipient for recipient in recipients])
        latest_recipients = Recipient.objects.order_by('-id')[:3]
        context["recipients_last"] = [message for message in latest_recipients]

        messages = Message.objects.all()
        context["messages_all"] = len([message for message in messages])
        latest_messages = Message.objects.order_by('-id')[:3]
        context["messages_last"] = [message for message in latest_messages]

        mailings = Mailing.objects.all()
        context["mailings_all"] = len([mailing for mailing in mailings])
        context["mailings_create"] = len([mailing for mailing in mailings if mailing.status == "Создана"])
        context["mailings_running"] = len([mailing for mailing in mailings if mailing.status == "Запущена"])
        context["mailings_completed"] = len([mailing for mailing in mailings if mailing.status == "Завершена"])

        sent_mailings = MailingAttempt.objects.all()

        if self.request.user.is_authenticated:
            context["sent_mailings_success"] = len([mailing for mailing in sent_mailings if mailing.status == 'success'])
            context["sent_mailings_error"] = len([mailing for mailing in sent_mailings if mailing.status == 'failure'])

            context["messages_success"] = MailingAttempt.objects.filter(
                status='success',
                mailing__owner=self.request.user,
            ).filter(
                Q(mailing__status=Mailing.STATUS_RUNNING) | Q(mailing__status=Mailing.STATUS_COMPLETED)
            ).count()
            return context

        return context


class RecipientListView(ListView):
    """ Класс представления списка получателей рассылки (клиентов) """
    model = Recipient
    template_name = "mailing_service/recipients_list.html"
    context_object_name = "page_object"
    paginate_by = 10
    ordering = ["created_at"]


class RecipientDetailView(DetailView):
    """ Класс представления детальной информации о получателе рассылки (клиенте) """
    model = Recipient
    template_name = "mailing_service/recipient_detail.html"
    context_object_name = "recipient"
    success_url = reverse_lazy("mailing_service:recipients_list")


class RecipientCreateView(CreateView):
    """ Класс создания получателя рассылки (клиента) """
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:recipients_list")
    extra_context = {
        "back_url": "mailing_service:recipients_list",
        "object_type": "Recipient",
    }


class RecipientUpdateView(UpdateView):
    """ Класс редактирования получателя рассылки (клиента) """
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:recipients_list")
    extra_context = {
        "back_url": "mailing_service:recipients_list",
        "object_type": "Recipient",
    }


class RecipientDeleteView(DeleteView):
    """ Класс удаления получателей рассылки (клиентов) """
    model = Recipient
    template_name = "mailing_service/confirm_delete.html"
    success_url = reverse_lazy("mailing_service:recipients_list")
    extra_context = {
        "back_url": "mailing_service:recipients_list",
        "object_type": "Recipient",
    }


class MessageListView(ListView):
    """ Класс просмотра списка сообщений """
    model = Message
    template_name = "mailing_service/messages_list.html"
    context_object_name = "page_object"
    paginate_by = 10
    ordering = ["created_at"]


class MessageDetailView(DetailView):
    """ Класс просмотра деталей сообщении """
    model = Message
    template_name = "mailing_service/message_detail.html"
    context_object_name = "message"
    success_url = reverse_lazy("mailing_service:messages_list")


class MessageCreateView(CreateView):
    """ Класс создания сообщения """
    model = Message
    form_class = MessageForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:messages_list")
    extra_context = {
        "back_url": "mailing_service:messages_list",
        "object_type": "Message",
    }


class MessageUpdateView(UpdateView):
    """ Класс редактирования сообщения """
    model = Message
    form_class = MessageForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:messages_list")
    extra_context = {
        "back_url": "mailing_service:messages_list",
        "object_type": "Message",
    }


class MessageDeleteView(DeleteView):
    """ Класс удаления сообщения """
    model = Message
    template_name = "mailing_service/confirm_delete.html"
    success_url = reverse_lazy("mailing_service:messages_list")
    extra_context = {
        "back_url": "mailing_service:messages_list",
        "object_type": "Message",
    }


class MailingListView(ListView):
    """ Класс просмотра списка рассылок """
    model = Mailing
    template_name = "mailing_service/mailings_list.html"
    context_object_name = "page_object"
    paginate_by = 10
    ordering = ["created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        for mailing in queryset:
            mailing.update_status()

        return queryset


class MailingDetailView(DetailView):
    """ Класс просмотра деталей о рассылке """
    model = Mailing
    template_name = "mailing_service/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(CreateView):
    """ Класс создания рассылки """
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:mailings_list")
    extra_context = {
        "back_url": "mailing_service:mailings_list",
        "object_type": "Mailing",
    }


class MailingUpdateView(UpdateView):
    """ Класс редактирования рассылки """
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:mailings_list")
    extra_context = {
        "back_url": "mailing_service:mailings_list",
        "object_type": "Mailing",
    }


class MailingDeleteView(DeleteView):
    """ Класс удаления рассылки """
    model = Mailing
    template_name = "mailing_service/confirm_delete.html"
    success_url = reverse_lazy("mailing_service:mailings_list")
    extra_context = {
        "back_url": "mailing_service:mailings_list",
        "object_type": "Mailing",
    }


class MailingStartView(View):
    """Класс запуска рассылки через POST-запрос и вывода ошибок"""

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)

        error_message = start_mailing(mailing)

        if error_message:
            messages.error(request, f"Ошибка при отправке: {error_message}")

        else:
            messages.success(request, "Рассылка успешно отправлена получателям!")

        return redirect('mailing_service:mailings_list')
