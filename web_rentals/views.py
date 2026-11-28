"""Представления аренды на основе Django ORM."""

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from web_bikes.models import Bike, Station

from .forms import (
    DEFAULT_SORT,
    STATUS_CHOICES,
    RentalFilterForm,
    RentalForm,
)
from .models import Rental, User

PAGE_SIZE = 5

# Сортировка по нескольким полям: кортеж передаётся в order_by().
SORT_FIELDS = {
    "date": ("-start_time", "pk"),
    "date_asc": ("start_time", "pk"),
    "bike": ("bike__model", "pk"),
    "user": ("user__name", "pk"),
    "station": ("station__name", "pk"),
}


def rentals_list_view(request):
    """Список аренд: фильтры, поиск, сортировка и пагинация."""
    form = RentalFilterForm(request.GET or None)

    if form.is_bound and form.is_valid():
        status = form.cleaned_data["status"] or "all"
        search = form.cleaned_data["search"].strip()
        selected_bike_obj = form.cleaned_data["bike"]
        selected_user_obj = form.cleaned_data["user"]
        selected_station_obj = form.cleaned_data["station"]
        sort = form.cleaned_data["sort"] or DEFAULT_SORT
    else:
        status = "all"
        search = ""
        selected_bike_obj = None
        selected_user_obj = None
        selected_station_obj = None
        sort = DEFAULT_SORT

    selected_bike = selected_bike_obj.pk if selected_bike_obj else None
    selected_user = selected_user_obj.pk if selected_user_obj else None
    selected_station = (
        selected_station_obj.pk if selected_station_obj else None
    )

    rentals = Rental.objects.with_related()

    # Фильтр по статусу аренды (менеджер скрывает условие фильтрации).
    if status == "active":
        rentals = rentals.active()
    elif status == "completed":
        rentals = rentals.completed()
    elif status == "cancelled":
        rentals = rentals.cancelled()
    else:
        status = "all"

    # Фильтры по связанным объектам (внешним ключам).
    if selected_bike is not None:
        rentals = rentals.filter(bike_id=selected_bike)

    if selected_user is not None:
        rentals = rentals.filter(user_id=selected_user)

    if selected_station is not None:
        rentals = rentals.filter(station_id=selected_station)

    # Поиск по полям связанных моделей через Q-объекты.
    if search:
        rentals = rentals.filter(
            Q(bike__model__icontains=search)
            | Q(user__name__icontains=search)
            | Q(user__email__icontains=search)
            | Q(station__name__icontains=search)
        )

    # Сортировка по нескольким полям.
    if sort not in SORT_FIELDS:
        sort = DEFAULT_SORT
    rentals = rentals.order_by(*SORT_FIELDS[sort])

    paginator = Paginator(rentals, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Агрегация: общее количество аренд по статусам.
    stats = Rental.objects.statistics()

    context = {
        "page_obj": page_obj,
        "rentals": page_obj.object_list,
        "stats": stats,
        "form": form,
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
        Rental.objects.with_related(),
        pk=rental_id,
    )
    user_rentals_count = rental.user.rentals.count()

    return render(
        request,
        "web_rentals/rental_detail.html",
        {"rental": rental, "user_rentals_count": user_rentals_count},
    )


def rental_create_view(request):
    """Оформить новую аренду через Django-форму."""
    if request.method == "POST":
        form = RentalForm(request.POST)

        if form.is_valid():
            bike = form.cleaned_data["bike"]

            # Проверка доступности велосипеда на момент создания аренды.
            bike_is_busy = Rental.objects.active().filter(bike=bike).exists()

            if not bike.is_available or bike_is_busy:
                form.add_error(
                    "bike",
                    "Этот велосипед уже находится в активной аренде.",
                )
            else:
                rental = form.save(commit=False)
                rental.status = Rental.Status.ACTIVE

                with transaction.atomic():
                    rental.save()
                    Bike.objects.filter(pk=bike.pk).update(
                        is_available=False
                    )

                return redirect(
                    "web_rentals:detail",
                    rental_id=rental.pk,
                )
    else:
        form = RentalForm(
            initial={"start_time": timezone.localtime()},
        )

    return render(
        request,
        "web_rentals/rental_form.html",
        {"form": form, "is_edit": False},
    )


def rental_update_view(request, rental_id):
    """Отредактировать активную аренду.

    При проверке занятости текущая аренда исключается из QuerySet,
    поэтому сохранение без смены велосипеда не считается конфликтом.
    """
    rental = get_object_or_404(
        Rental.objects.active(),
        pk=rental_id,
    )
    old_bike_id = rental.bike_id

    if request.method == "POST":
        form = RentalForm(request.POST, instance=rental)

        if form.is_valid():
            new_bike = form.cleaned_data["bike"]
            bike_changed = new_bike.pk != old_bike_id

            # Исключаем редактируемую аренду из проверки занятости.
            bike_is_busy = (
                Rental.objects.active()
                .filter(bike=new_bike)
                .exclude(pk=rental.pk)
                .exists()
            )

            if bike_is_busy or (bike_changed and not new_bike.is_available):
                form.add_error(
                    "bike",
                    "Выбранный велосипед уже находится в активной аренде.",
                )
            else:
                with transaction.atomic():
                    updated = form.save(commit=False)
                    updated.status = Rental.Status.ACTIVE
                    updated.save()

                    Bike.objects.filter(pk=new_bike.pk).update(
                        is_available=False
                    )

                    if bike_changed:
                        Bike.objects.filter(pk=old_bike_id).update(
                            is_available=True
                        )

                return redirect(
                    "web_rentals:detail",
                    rental_id=rental.pk,
                )
    else:
        form = RentalForm(instance=rental)

    return render(
        request,
        "web_rentals/rental_form.html",
        {"form": form, "rental": rental, "is_edit": True},
    )


@require_POST
def rental_cancel_view(request, rental_id):
    """Отменить активную аренду и вернуть велосипед в парк."""
    rental = get_object_or_404(
        Rental.objects.active(),
        pk=rental_id,
    )
    rental.cancel()

    return redirect("web_rentals:detail", rental_id=rental.pk)


@require_POST
def rental_complete_view(request, rental_id):
    """Завершить аренду и вернуть велосипед на станцию."""
    rental = get_object_or_404(Rental, pk=rental_id)
    rental.complete()

    return redirect("web_rentals:detail", rental_id=rental.pk)


def rental_statistics_view(request):
    """Статистика по станциям, клиентам и типам велосипедов."""
    station_stats = Station.objects.with_rental_stats().order_by(
        "-rentals_total",
        "name",
    )

    user_stats = User.objects.with_rental_stats().order_by(
        "-rentals_total",
        "name",
    )

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

    # aggregate(): сводные показатели по всей базе одним запросом.
    summary = Rental.objects.statistics()
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
