from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("web_main.urls")),
    path("bikes/", include("web_bikes.urls")),
    path("rentals/", include("web_rentals.urls")),
]

# В режиме разработки Django отдаёт загруженные изображения сам.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

# Маршруты Django Debug Toolbar подключаются только при локальной разработке.
if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]

# Кастомная страница ошибки 404 (используется при DEBUG = False).
handler404 = "web_main.views.page_not_found"
