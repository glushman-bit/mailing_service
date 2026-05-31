from django.contrib.auth.views import LoginView, LogoutView

from django.urls import path
from .apps import UsersConfig

from .views import UserCreateView, UserDetailView, UserUpdateView, email_verification, UserListView, \
    ToggleUserActiveView

app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page="mailing_service:main_page"), name='logout'),
    path('register/', UserCreateView.as_view(), name='register'),
    path('email-confirm/<str:token>/', email_verification, name='email_confirm'),
    path('profile/', UserDetailView.as_view(), name='profile'),
    path('profile/update/', UserUpdateView.as_view(), name='profile_update'),
    path('users-list/', UserListView.as_view(), name='users_list'),
    path('<int:pk>/toggle-active/', ToggleUserActiveView.as_view(), name='toggle_user_active'),
]
