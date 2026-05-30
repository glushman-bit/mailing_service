import secrets

from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.contrib import messages

from config.settings import EMAIL_HOST_USER
from users.models import User
from users.forms import UserRegistrationForm, UserProfileForm



class UserCreateView(SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    success_message = "Регистрация успешна! Письмо со ссылкой для подтверждения отправлено на вашу почту."

    def form_valid(self, form):
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
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()

    messages.success(request, 'Ваша почта успешно подтверждена! Теперь вы можете войти.')
    return redirect(reverse('login'))


class UserDetailView(DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user


class UserUpdateView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_form.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


