from django.contrib import admin
from mailing_service.models import Recipient, Message, Mailing


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'comment')
    search_fields = ('email', 'full_name', 'comment')
    list_filter = ('email',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('title','content',)
    search_fields = ('title', 'content',)
    list_filter = ('title',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('message', 'status')
    search_fields = ('message', 'status')
    list_filter = ('message', 'status')
