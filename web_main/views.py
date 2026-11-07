"""Главная страница сервиса Bikely."""

from django.db.models import Avg, Count, Q
from django.shortcuts import render

from web_bikes.models import Bike, Station
from web_rentals.models import Rental


def index(request):
    """Главная страница: станции и сводные показатели сервиса."""
    stations = Station.objects.annotate(
        rentals_count=Count("rentals"),
    ).order_by("-capacity", "name")

    stats = Bike.objects.aggregate(
        bikes_total=Count("id"),
        bikes_available=Count("id", filter=Q(is_available=True)),
    )
    stats.update(
        Station.objects.aggregate(
            stations_total=Count("id"),
            average_capacity=Avg("capacity"),
        )
    )
    stats["rentals_total"] = Rental.objects.count()
    stats["rentals_active"] = Rental.objects.filter(
        is_completed=False
    ).count()

    return render(
        request,
        "web_main/index.html",
        {"stations": stations, "stats": stats},
    )


def page_not_found(request, exception=None):
    """Кастомная страница ошибки 404."""
    return render(request, "404.html", status=404)
