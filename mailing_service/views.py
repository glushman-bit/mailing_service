from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from mailing_service.forms import MailingForm, MessageForm, RecipientForm
from mailing_service.models import Mailing, MailingAttempt, Message, Recipient
from mailing_service.services import start_mailing


class MainPageView(TemplateView):
    """Класс вывода главной страницы с разграничением статистики администратора и пользователей"""

    template_name = "mailing_service/main_page.html"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Mailing.objects.filter(owner=self.request.user)
        return Mailing.objects.none()

    def get_context_data(self, **kwargs):
        """Добавление данных на главную страницу"""
        context = super().get_context_data(**kwargs)
        current_user = self.request.user

        if current_user.is_authenticated:

            if self.request.user.is_superuser or self.request.user.is_staff:
                user_recipients = Recipient.objects.all()
                user_messages = Message.objects.all()
                user_mailings = Mailing.objects.all()
                user_attempt = MailingAttempt.objects.all()

            else:
                user_recipients = Recipient.objects.filter(owner=current_user)
                user_messages = Message.objects.filter(owner=current_user)
                user_mailings = Mailing.objects.filter(owner=current_user)
                user_attempt = MailingAttempt.objects.filter(mailing__owner=current_user)

            context["recipients_all"] = user_recipients.count()
            context["recipients_last"] = user_recipients.order_by("-id")[:3]

            context["messages_all"] = user_messages.count()
            context["messages_last"] = user_messages.order_by("-id")[:3]

            user_mailings_stats = user_mailings.aggregate(
                all_count=Count("id"),
                create_count=Count("id", filter=Q(status=Mailing.STATUS_CREATED)),
                running_count=Count("id", filter=Q(status=Mailing.STATUS_RUNNING)),
                completed_count=Count("id", filter=Q(status=Mailing.STATUS_COMPLETED)),
            )
            context["mailings_all"] = user_mailings_stats["all_count"]
            context["mailings_create"] = user_mailings_stats["create_count"]
            context["mailings_running"] = user_mailings_stats["running_count"]
            context["mailings_completed"] = user_mailings_stats["completed_count"]
            context["messages_success"] = user_attempt.filter(status="success").count()
            context["messages_failure"] = user_attempt.filter(status="failure").count()
            context["sent_mailings_success"] = (
                user_attempt.filter(status="success").values("run_id").distinct().order_by().count()
            )
            context["sent_mailings_error"] = (
                user_attempt.filter(status="failure").values("run_id").distinct().order_by().count()
            )

        else:
            context["recipients_all"] = 0
            context["recipients_last"] = []
            context["messages_all"] = 0
            context["messages_last"] = []
            context["mailings_all"] = 0
            context["mailings_create"] = 0
            context["mailings_running"] = 0
            context["mailings_completed"] = 0
            context["sent_mailings_success"] = 0
            context["sent_mailings_error"] = 0
            context["messages_success"] = 0

        return context


class RecipientListView(ListView):
    """Класс представления списка получателей рассылки (клиентов)"""

    model = Recipient
    template_name = "mailing_service/recipients_list.html"
    context_object_name = "page_object"
    paginate_by = 20
    ordering = ["created_at"]

    def get_queryset(self):
        """Вывод списка получателей рассылки как владельца или как администратора"""
        user = self.request.user

        if user.is_superuser or user.is_staff:
            cache_key = "recipients_list_admin"

        else:
            cache_key = f"recipients_list_user_{user.id}"

        queryset = cache.get(cache_key)

        if queryset is None:
            if user.is_superuser or user.is_staff:
                queryset = Recipient.objects.all().order_by("owner")
            else:
                queryset = Recipient.objects.filter(owner=user)

            cache.set(cache_key, queryset, 300)

        return queryset


@method_decorator(cache_page(60 * 5), name="dispatch")
class RecipientDetailView(DetailView):
    """Класс представления детальной информации о получателе рассылки (клиенте)"""

    model = Recipient
    template_name = "mailing_service/recipient_detail.html"
    context_object_name = "recipient"
    success_url = reverse_lazy("mailing_service:recipients_list")


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Класс создания получателя рассылки (клиента)"""

    model = Recipient
    form_class = RecipientForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:recipients_list")
    extra_context = {
        "back_url": "mailing_service:recipients_list",
        "object_type": "Recipient",
    }

    def form_valid(self, form):
        """Автоматическая привязка пользователя как владельца получателя рассылки"""
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """Класс редактирования получателя рассылки (клиента)"""

    model = Recipient
    form_class = RecipientForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:recipients_list")
    extra_context = {
        "back_url": "mailing_service:recipients_list",
        "object_type": "Recipient",
    }


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    """Класс удаления получателей рассылки (клиентов)"""

    model = Recipient
    template_name = "mailing_service/confirm_delete.html"
    success_url = reverse_lazy("mailing_service:recipients_list")
    extra_context = {
        "back_url": "mailing_service:recipients_list",
        "object_type": "Recipient",
    }


class MessageListView(ListView):
    """Класс просмотра списка сообщений"""

    model = Message
    template_name = "mailing_service/messages_list.html"
    context_object_name = "page_object"
    paginate_by = 20
    ordering = ["created_at"]

    def get_queryset(self):
        """Вывод списка получателей рассылки как владельца или как администратора"""
        user = self.request.user

        if user.is_superuser or user.is_staff:
            cache_key = "message_list_admin"

        else:
            cache_key = f"message_list_user_{user.id}"

        queryset = cache.get(cache_key)

        if queryset is None:
            if user.is_superuser or user.is_staff:
                queryset = Message.objects.all().order_by("owner")
            else:
                queryset = Message.objects.filter(owner=user)

            cache.set(cache_key, queryset, 300)

        return queryset


@method_decorator(cache_page(60 * 5), name="dispatch")
class MessageDetailView(DetailView):
    """Класс просмотра деталей сообщении"""

    model = Message
    template_name = "mailing_service/message_detail.html"
    context_object_name = "message"
    success_url = reverse_lazy("mailing_service:messages_list")


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Класс создания сообщения"""

    model = Message
    form_class = MessageForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:messages_list")
    extra_context = {
        "back_url": "mailing_service:messages_list",
        "object_type": "Message",
    }

    def form_valid(self, form):
        """Создание текущего пользователя как владельца сообщения"""
        messages = form.save()
        user = self.request.user
        messages.owner = user
        messages.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """Класс редактирования сообщения"""

    model = Message
    form_class = MessageForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:messages_list")
    extra_context = {
        "back_url": "mailing_service:messages_list",
        "object_type": "Message",
    }


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """Класс удаления сообщения"""

    model = Message
    template_name = "mailing_service/confirm_delete.html"
    success_url = reverse_lazy("mailing_service:messages_list")
    extra_context = {
        "back_url": "mailing_service:messages_list",
        "object_type": "Message",
    }


class MailingListView(ListView):
    """Класс просмотра списка рассылок"""

    model = Mailing
    template_name = "mailing_service/mailings_list.html"
    context_object_name = "page_object"
    paginate_by = 20

    def get_queryset(self):
        """Вывод списка получателей рассылки как владельца или как администратора с обновлением статуса"""
        if self.request.user.is_superuser or self.request.user.is_staff:
            queryset = Mailing.objects.all().order_by("owner")
        else:
            queryset = Mailing.objects.filter(owner=self.request.user)

        for mailing in queryset:
            mailing.update_status()

        return queryset.order_by("-end_time")


@method_decorator(cache_page(60 * 5), name="dispatch")
class MailingDetailView(DetailView):
    """Класс просмотра деталей о рассылке"""

    model = Mailing
    template_name = "mailing_service/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        """Обновление статуса в детализации рассылки"""
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Класс создания рассылки"""

    model = Mailing
    form_class = MailingForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:mailings_list")
    extra_context = {
        "back_url": "mailing_service:mailings_list",
        "object_type": "Mailing",
    }

    def get_form(self, form_class=None):
        """Фильтруем выпадающие списки внутри формы"""
        form = super().get_form(form_class)
        if not self.request.user.is_superuser:
            form.fields["message"].queryset = Message.objects.filter(owner=self.request.user)
            form.fields["recipients"].queryset = Recipient.objects.filter(owner=self.request.user)

        return form

    def form_valid(self, form):
        """Создание текущего пользователя как владельца рассылки"""
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(UpdateView):
    """Класс редактирования рассылки"""

    model = Mailing
    form_class = MailingForm
    template_name = "mailing_service/form.html"
    success_url = reverse_lazy("mailing_service:mailings_list")
    extra_context = {
        "back_url": "mailing_service:mailings_list",
        "object_type": "Mailing",
    }


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Класс удаления рассылки"""

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


class MailingDistributionView(LoginRequiredMixin, View):
    """Класс отключения рассылки"""

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        user = request.user

        is_owner = mailing.owner == user
        is_superuser = user.is_superuser
        has_perms = user.has_perm("mailing.can_disable_distribution")

        if not (is_owner or is_superuser or has_perms):
            return HttpResponseForbidden("У вас не доступа для отключения рассылки.")

        mailing.end_time = timezone.now()
        messages.success(request, "Рассылка успешно отключена!")
        mailing.save()

        return redirect("mailing_service:mailings_list")
