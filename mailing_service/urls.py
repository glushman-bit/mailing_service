from django.urls import path
from mailing_service.views import MainPageView, RecipientListView, MessageListView, MailingListView, \
    RecipientDetailView, RecipientCreateView, RecipientUpdateView, RecipientDeleteView, MessageDetailView, \
    MessageCreateView, MessageUpdateView, MessageDeleteView, MailingDetailView, MailingCreateView, MailingUpdateView, \
    MailingDeleteView
from mailing_service.apps import MailingServiceConfig


app_name = MailingServiceConfig.name

urlpatterns = [
    path('', MainPageView.as_view(), name='main_page'),

    path('recipients/', RecipientListView.as_view(), name='recipients_list'),
    path('recipient/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipient/new/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipient/<int:pk>/update/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipient/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),

    path('messages/', MessageListView.as_view(), name='messages_list'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('message/new/', MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/update/', MessageUpdateView.as_view(), name='message_update'),
    path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

    path('mailings/', MailingListView.as_view(), name='mailings_list'),
    path('mailing/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailing/new/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailing/<int:pk>/update/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailing/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
]
