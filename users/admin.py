from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "is_active",
        "is_superuser",
        "is_staff",
        "created_at",
    )
    exclude = ("password",)
    search_fields = ("email",)
