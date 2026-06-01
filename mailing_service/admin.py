from django.contrib import admin

from .models import Mailing, MailingAttempt, Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'comment', 'created_at')
    search_fields = ('email', 'full_name', 'comment')
    list_filter = ('email', 'created_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content', 'created_at')
    search_fields = (
        'title',
        'content',
    )
    list_filter = ('title', 'created_at')


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'status', 'created_at')
    search_fields = ('message', 'status')
    list_filter = ('message', 'status', 'created_at')


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'mailing',
        'attempt_time',
        'status',
        'server_response',
    )
    search_fields = ('mailing', 'status')
    list_filter = ('mailing', 'status', 'attempt_time')
