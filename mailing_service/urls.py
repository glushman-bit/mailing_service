from django.urls import path
from mailing_service.views import MainPageView, RecipientListView, MessageListView, MailingListView, \
    RecipientDetailView, RecipientCreateView, RecipientUpdateView, RecipientDeleteView
from mailing_service.apps import MailingServiceConfig


app_name = MailingServiceConfig.name

urlpatterns = [
    path('', MainPageView.as_view(), name='main_page'),
    path('recipients/', RecipientListView.as_view(), name='recipients_list'),
    path('recipients/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipients/new/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/<int:pk>/update/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipients/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),

    path('messages/', MessageListView.as_view(), name='messages_list'),

    path('mailings/', MailingListView.as_view(), name='mailings_list'),
]
