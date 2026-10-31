
from django.shortcuts import render

from storage import (
    load_bikes,
    load_users,
    load_stations,
    load_rentals,
)


def get_rental_by_id(rentals_list, rental_id):
    """Найти аренду по идентификатору."""
    for rental in rentals_list:
        if rental.id == rental_id:
            return rental
    return None


def get_all_rentals():
    """Загрузить аренды вместе со связанными объектами."""
    bikes = load_bikes("data/bikes.json")
    users = load_users("data/users.json")
    stations = load_stations("data/stations.json")

    return load_rentals(
        "data/rentals.json",
        bikes,
        users,
        stations,
    )


def rentals_list_view(request):
    """Показать список всех аренд."""
    rentals = get_all_rentals()

    context = {
        "rentals": rentals,
    }

    return render(request, "web_rentals/rental_list.html", context)


def rental_detail_view(request, rental_id):
    """Показать подробную информацию об аренде."""
    rentals = get_all_rentals()
    rental = get_rental_by_id(rentals, rental_id)

    context = {
        "rental": rental,
    }

    return render(
        request,
        "web_rentals/rental_detail.html",
        context,
        status=404 if rental is None else 200,
    )
