import secrets

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import PermissionsMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from config.settings import EMAIL_HOST_USER
from users.forms import UserProfileForm, UserRegistrationForm
from users.models import User


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Класс просмотра списка пользователей сервиса для Администраторов и Менеджеров"""
    model = User
    template_name = 'users/users_list.html'
    context_object_name = 'users_list'

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name='Менеджеры').exists()


class UserCreateView(SuccessMessageMixin, CreateView):
    """Класс создания пользователя"""
    model = User
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    success_message = "Регистрация успешна! Письмо со ссылкой для подтверждения отправлено на вашу почту."

    def form_valid(self, form):
        """Отправка сообщения на электронную почту для авторизации"""
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(20)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"

        send_mail(
            subject="Подтверждение почты",
            message=f"Привет, {user.email}, перейди по ссылке для подтверждения почты: {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        return super().form_valid(form)

def email_verification(request, token):
    """Вывод информации об успешной авторизации"""
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()

    messages.success(request, 'Ваша почта успешно подтверждена! Теперь вы можете войти.')
    return redirect(reverse('login'))


class UserDetailView(DetailView):
    """Класс просмотра детальной информации о пользователе"""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user


class UserUpdateView(UpdateView):
    """Класс обновления информации о пользователи"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_form.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class ToggleUserActiveView(View):
    """Контроллер для блокировки/разблокировки пользователей менеджером"""

    def test_func(self):
        """Разрешение действия только для суперпользователя или персонала"""
        return self.request.user.is_superuser or self.request.user.is_staff

    def post(self, request, pk, *args, **kwargs):
        user_toggle = get_object_or_404(User, pk=pk)

        if user_toggle == request.user:
            messages.error(request, "Вы не можете заблокировать самого себя!")
            return redirect(reverse('users:users_list'))

        if user_toggle.is_superuser:
            messages.error(request, "Нельзя заблокировать администратора сайта!")
            return redirect(reverse('users:users_list'))

        if user_toggle.is_active:
            user_toggle.is_active = False
            messages.error(request, f'Пользователь {user_toggle.email} успешно заблокирован.')

        else:
            user_toggle.is_active = True
            messages.success(request, f'Пользователь {user_toggle.email} успешно разблокирован.')

        user_toggle.save()

        return redirect(reverse('users:users_list'))
