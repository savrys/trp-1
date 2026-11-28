"""Представления каталога велосипедов на основе Django ORM."""

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DEFAULT_SORT, BikeFilterForm, BikeForm
from .models import Bike, Station

# Сортировка по нескольким полям: кортеж передаётся в order_by().
SORT_FIELDS = {
    "model": ("model", "pk"),
    "-model": ("-model", "pk"),
    "type": ("type", "model"),
    "-type": ("-type", "-model"),
    "availability": ("-is_available", "model"),
}


def bikes_list_view(request):
    """Список велосипедов с поиском, фильтрацией и сортировкой."""
    form = BikeFilterForm(request.GET or None)

    if form.is_bound and form.is_valid():
        search = form.cleaned_data["search"].strip()
        selected_type = form.cleaned_data["type"]
        availability = form.cleaned_data["availability"] or "all"
        sort = form.cleaned_data["sort"] or DEFAULT_SORT
    else:
        search = ""
        selected_type = ""
        availability = "all"
        sort = DEFAULT_SORT

    bikes = Bike.objects.with_rental_stats()

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
        bikes = bikes.available()
    elif availability == "rented":
        bikes = bikes.exclude(is_available=True)
    else:
        availability = "all"

    if sort not in SORT_FIELDS:
        sort = DEFAULT_SORT
    bikes = bikes.order_by(*SORT_FIELDS[sort])

    stations = Station.objects.with_rental_stats()

    context = {
        "bikes": bikes,
        "stations": stations,
        "form": form,
        "search": search,
        "selected_type": selected_type,
        "selected_type_label": selected_type_label,
        "availability": availability,
        "sort": sort,
    }
    return render(request, "web_bikes/bike_list.html", context)


def bike_detail_view(request, slug):
    """Подробная информация о велосипеде и история его аренды."""
    bike = get_object_or_404(Bike.objects.with_rental_stats(), slug=slug)
    rental_history = (
        bike.rentals.with_related().order_by("-start_time", "pk")
    )

    return render(
        request,
        "web_bikes/bike_detail.html",
        {"bike": bike, "rental_history": rental_history},
    )


def bike_create_view(request):
    """Добавить велосипед в парк через форму с загрузкой изображения."""
    if request.method == "POST":
        form = BikeForm(request.POST, request.FILES)

        if form.is_valid():
            bike = form.save()
            return redirect("web_bikes:detail", slug=bike.slug)
    else:
        form = BikeForm()

    return render(
        request,
        "web_bikes/bike_form.html",
        {"form": form, "is_edit": False},
    )


def bike_update_view(request, slug):
    """Отредактировать велосипед и при необходимости заменить изображение."""
    bike = get_object_or_404(Bike, slug=slug)

    if request.method == "POST":
        form = BikeForm(request.POST, request.FILES, instance=bike)

        if form.is_valid():
            bike = form.save()
            return redirect("web_bikes:detail", slug=bike.slug)
    else:
        form = BikeForm(instance=bike)

    return render(
        request,
        "web_bikes/bike_form.html",
        {"form": form, "bike": bike, "is_edit": True},
    )
