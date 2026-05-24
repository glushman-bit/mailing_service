from django.urls import path
from mailing_service.views import MainPageView
from mailing_service.apps import MailingServiceConfig


app_name = MailingServiceConfig.name

urlpatterns = [
    path('', MainPageView.as_view(), name='main_page'),
]
