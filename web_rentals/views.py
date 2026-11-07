"""Представления аренды на основе Django ORM."""

from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from web_bikes.models import Bike, Station

from .models import Rental, User

PAGE_SIZE = 5
DEFAULT_SORT = "date"

# Сортировка по нескольким полям: кортеж передаётся в order_by().
SORT_FIELDS = {
    "date": ("-start_time", "pk"),
    "date_asc": ("start_time", "pk"),
    "bike": ("bike__model", "pk"),
    "user": ("user__name", "pk"),
    "station": ("station__name", "pk"),
}

STATUS_CHOICES = (
    ("all", "Все аренды"),
    ("active", "Активные"),
    ("completed", "Завершённые"),
)


def _to_int(value):
    """Привести GET-параметр к int (или вернуть None)."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def rentals_list_view(request):
    """Список аренд: фильтры, поиск, сортировка и пагинация."""
    rentals = Rental.objects.select_related("bike", "user", "station")

    # Фильтр по статусу аренды.
    status = request.GET.get("status", "all")
    if status == "active":
        rentals = rentals.filter(is_completed=False)
    elif status == "completed":
        rentals = rentals.filter(is_completed=True)
    else:
        status = "all"

    # Фильтры по связанным объектам (внешним ключам).
    selected_bike = _to_int(request.GET.get("bike"))
    if selected_bike is not None:
        rentals = rentals.filter(bike_id=selected_bike)

    selected_user = _to_int(request.GET.get("user"))
    if selected_user is not None:
        rentals = rentals.filter(user_id=selected_user)

    selected_station = _to_int(request.GET.get("station"))
    if selected_station is not None:
        rentals = rentals.filter(station_id=selected_station)

    # Поиск по полям связанных моделей через Q-объекты.
    search = request.GET.get("search", "").strip()
    if search:
        rentals = rentals.filter(
            Q(bike__model__icontains=search)
            | Q(user__name__icontains=search)
            | Q(user__email__icontains=search)
            | Q(station__name__icontains=search)
        )

    # Сортировка по нескольким полям.
    sort = request.GET.get("sort", DEFAULT_SORT)
    if sort not in SORT_FIELDS:
        sort = DEFAULT_SORT
    rentals = rentals.order_by(*SORT_FIELDS[sort])

    paginator = Paginator(rentals, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Агрегация: общее количество аренд по статусам.
    stats = Rental.objects.aggregate(
        total=Count("id"),
        active=Count("id", filter=Q(is_completed=False)),
        completed=Count("id", filter=Q(is_completed=True)),
    )

    context = {
        "page_obj": page_obj,
        "rentals": page_obj.object_list,
        "stats": stats,
        "status": status,
        "search": search,
        "sort": sort,
        "selected_bike": selected_bike,
        "selected_user": selected_user,
        "selected_station": selected_station,
        "bikes": Bike.objects.order_by("model"),
        "users": User.objects.order_by("name"),
        "stations": Station.objects.order_by("name"),
        "statuses": STATUS_CHOICES,
    }
    return render(request, "web_rentals/rental_list.html", context)


def rental_detail_view(request, rental_id):
    """Подробная информация об аренде."""
    rental = get_object_or_404(
        Rental.objects.select_related("bike", "user", "station"),
        pk=rental_id,
    )
    user_rentals_count = rental.user.rentals.count()

    return render(
        request,
        "web_rentals/rental_detail.html",
        {"rental": rental, "user_rentals_count": user_rentals_count},
    )


@require_POST
def rental_complete_view(request, rental_id):
    """Завершить аренду и вернуть велосипед на станцию."""
    rental = get_object_or_404(Rental, pk=rental_id)
    rental.complete()

    return redirect("web_rentals:detail", rental_id=rental.pk)


def rental_statistics_view(request):
    """Статистика по станциям, клиентам и типам велосипедов."""
    station_stats = Station.objects.annotate(
        rentals_total=Count("rentals"),
        rentals_active=Count(
            "rentals",
            filter=Q(rentals__is_completed=False),
        ),
    ).order_by("-rentals_total", "name")

    user_stats = User.objects.annotate(
        rentals_total=Count("rentals"),
        rentals_active=Count(
            "rentals",
            filter=Q(rentals__is_completed=False),
        ),
    ).order_by("-rentals_total", "name")

    # values() + annotate(): сводка по типам велосипедов.
    type_labels = dict(Bike.Type.choices)
    type_stats = list(
        Bike.objects.values("type")
        .annotate(
            total=Count("id"),
            available=Count("id", filter=Q(is_available=True)),
        )
        .order_by("-total", "type")
    )
    for item in type_stats:
        item["type_label"] = type_labels.get(item["type"], item["type"])

    # aggregate(): сводные показатели по всей базе.
    summary = Rental.objects.aggregate(
        total=Count("id"),
        active=Count("id", filter=Q(is_completed=False)),
        completed=Count("id", filter=Q(is_completed=True)),
        last_start_time=Max("start_time"),
    )
    summary["average_capacity"] = Station.objects.aggregate(
        value=Avg("capacity")
    )["value"]

    return render(
        request,
        "web_rentals/rental_statistics.html",
        {
            "station_stats": station_stats,
            "user_stats": user_stats,
            "type_stats": type_stats,
            "summary": summary,
        },
    )
