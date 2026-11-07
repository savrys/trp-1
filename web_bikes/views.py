"""Представления каталога велосипедов на основе Django ORM."""

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Bike, Station

DEFAULT_SORT = "model"

# Сортировка по нескольким полям: кортеж передаётся в order_by().
SORT_FIELDS = {
    "model": ("model", "pk"),
    "-model": ("-model", "pk"),
    "type": ("type", "model"),
    "-type": ("-type", "-model"),
    "availability": ("-is_available", "model"),
}

AVAILABILITY_CHOICES = (
    ("all", "Все велосипеды"),
    ("available", "Свободные"),
    ("rented", "На руках у клиентов"),
)


def bikes_list_view(request):
    """Список велосипедов с поиском, фильтрацией и сортировкой."""
    search = request.GET.get("search", "").strip()
    selected_type = request.GET.get("type", "").strip()
    availability = request.GET.get("availability", "all")
    sort = request.GET.get("sort", DEFAULT_SORT)

    bikes = Bike.objects.all()

    # Поиск сразу по нескольким полям через Q-объекты.
    if search:
        bikes = bikes.filter(
            Q(model__icontains=search) | Q(type__icontains=search)
        )

    # Фильтрация по типу велосипеда (только допустимые значения).
    type_labels = dict(Bike.Type.choices)
    if selected_type in type_labels:
        bikes = bikes.filter(type=selected_type)
        selected_type_label = type_labels[selected_type]
    else:
        selected_type = ""
        selected_type_label = ""

    # Фильтрация по доступности: filter() и exclude().
    if availability == "available":
        bikes = bikes.filter(is_available=True)
    elif availability == "rented":
        bikes = bikes.exclude(is_available=True)
    else:
        availability = "all"

    if sort not in SORT_FIELDS:
        sort = DEFAULT_SORT
    bikes = bikes.order_by(*SORT_FIELDS[sort])

    stations = Station.objects.annotate(
        rentals_count=Count("rentals"),
    )

    context = {
        "bikes": bikes,
        "stations": stations,
        "search": search,
        "selected_type": selected_type,
        "selected_type_label": selected_type_label,
        "availability": availability,
        "sort": sort,
        "bike_types": Bike.Type.choices,
        "availability_choices": AVAILABILITY_CHOICES,
    }
    return render(request, "web_bikes/bike_list.html", context)


def bike_detail_view(request, bike_id):
    """Подробная информация о велосипеде и история его аренды."""
    bike = get_object_or_404(Bike, pk=bike_id)
    rental_history = bike.rentals.select_related("user", "station")

    return render(
        request,
        "web_bikes/bike_detail.html",
        {"bike": bike, "rental_history": rental_history},
    )

