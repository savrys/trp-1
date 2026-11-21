"""Главная страница сервиса Bikely."""

from django.shortcuts import render

from web_bikes.models import Station


def index(request):
    """Главная страница: станции и сводные показатели сервиса.

    Общие показатели сервиса приходят из контекстного процессора
    ``web_main.context_processors.bikely_context``, поэтому в представлении
    остаётся только список станций с количеством аренд.
    """
    stations = Station.objects.with_rental_stats().order_by(
        "-capacity",
        "name",
    )

    return render(
        request,
        "web_main/index.html",
        {"stations": stations},
    )


def page_not_found(request, exception=None):
    """Кастомная страница ошибки 404."""
    return render(request, "404.html", status=404)
