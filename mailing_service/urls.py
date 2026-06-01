from django.urls import path
from django.views.generic import TemplateView

from mailing_service.apps import MailingServiceConfig
from mailing_service.views import (
    MailingCreateView,
    MailingDeleteView,
    MailingDetailView,
    MailingDistributionView,
    MailingListView,
    MailingStartView,
    MailingUpdateView,
    MainPageView,
    MessageCreateView,
    MessageDeleteView,
    MessageDetailView,
    MessageListView,
    MessageUpdateView,
    RecipientCreateView,
    RecipientDeleteView,
    RecipientDetailView,
    RecipientListView,
    RecipientUpdateView,
)

app_name = MailingServiceConfig.name

urlpatterns = [
    path('', MainPageView.as_view(), name='main_page'),
    # Ссылки на страницы получателей рассылок
    path('recipients/', RecipientListView.as_view(), name='recipients_list'),
    path('recipient/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipient/new/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipient/<int:pk>/update/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipient/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),
    # Ссылки на страницы писем
    path('messages/', MessageListView.as_view(), name='messages_list'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('message/new/', MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/update/', MessageUpdateView.as_view(), name='message_update'),
    path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    # Ссылки на страницы рассылок
    path('mailings/', MailingListView.as_view(), name='mailings_list'),
    path('mailing/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailing/new/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailing/<int:pk>/update/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailing/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    # Ссылка на страницу отправки рассылок
    path('send/<int:pk>/', MailingStartView.as_view(), name='send_start'),
    # Прочие ссылки
    path('info/', TemplateView.as_view(template_name='mailing_service/info.html'), name='info'),
    path('mailing/<int:pk>/disable/', MailingDistributionView.as_view(), name='toggle_mailing'),
]
