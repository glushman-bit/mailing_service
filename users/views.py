import secrets

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, UpdateView
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER
from users.models import User
from users.forms import UserRegistrationForm



class UserCreateView(CreateView):
    model = User
    form_class = UserRegistrationForm
    success_url = reverse_lazy('users:login')

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

    return redirect(reverse('users:login'))


class UserDetailView(DetailView):
    model = User
    template_name = 'users/profile.html'

    def get_object(self, queryset=None):
        return self.request.user


class UserUpdateView(UpdateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/profile_form.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


