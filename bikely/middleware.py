"""Middleware проекта Bikely."""

from django.conf import settings

# Адреса, для которых стандартные страницы ошибок Django остаются как есть.
EXCLUDED_PREFIXES = ("/admin/", "/static/")


class Custom404Middleware:
    """Показывать фирменную страницу 404 и при включённом DEBUG.

    В режиме отладки Django подменяет ответ 404 технической страницей
    с отладочной информацией. Middleware заменяет такой ответ шаблоном
    templates/404.html, чтобы пользователь всегда видел оформленную
    страницу «Страница не найдена».
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (
            settings.DEBUG
            and response.status_code == 404
            and not request.path.startswith(EXCLUDED_PREFIXES)
        ):
            # Локальный импорт, чтобы не обращаться к моделям
            # до готовности реестра приложений Django.
            from web_main.views import page_not_found

            return page_not_found(request)

        return response
