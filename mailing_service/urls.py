from django.urls import path
from mailing_service.views import MainPageView, RecipientListView, MessageListView, MailingListView
from mailing_service.apps import MailingServiceConfig


app_name = MailingServiceConfig.name

urlpatterns = [
    path('', MainPageView.as_view(), name='main_page'),
    path('recipients/', RecipientListView.as_view(), name='recipients_list'),

    path('messages/', MessageListView.as_view(), name='messages_list'),

    path('mailings/', MailingListView.as_view(), name='mailings_list'),
]
