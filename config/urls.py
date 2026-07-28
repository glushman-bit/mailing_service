from django.contrib import admin
from django.urls import include
from django.urls import path
from django.conf.urls.static import static
from config import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('mailing/', include('mailing_service.urls', namespace='mailing')),
    path('users/', include('users.urls', namespace='users')),

# 1. Подключаем ВСЕ встроенные маршруты авторизации (вход, выход, сброс пароля)
    path('accounts/', include('django.contrib.auth.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
