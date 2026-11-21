"""Настройки доступа к Django Debug Toolbar."""

from django.conf import settings


def show_toolbar(request):
    """Показывать панель отладки только при локальной разработке.

    Тестовый клиент Django обращается к хосту ``testserver``, поэтому
    панель не появляется в ответах автоматизированных тестов.
    """
    if not settings.DEBUG:
        return False

    host = request.get_host().split(":")[0]
    return host in {"127.0.0.1", "localhost"}
