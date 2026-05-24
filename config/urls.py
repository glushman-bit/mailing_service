from django.contrib import admin
from django.urls import include
from django.urls import path
from django.conf.urls.static import static
from config import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('mailing/', include('mailing_service.urls', namespace='mailing')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
