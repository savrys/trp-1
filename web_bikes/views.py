
from django.shortcuts import render

from storage import load_bikes, load_stations


def get_bike_by_id(bikes_list, bike_id):
    """Найти велосипед по идентификатору."""
    for bike in bikes_list:
        if bike.id == bike_id:
            return bike
    return None


def bikes_list_view(request):
    """Показать список велосипедов и станций."""
    bikes = load_bikes("data/bikes.json")
    stations = load_stations("data/stations.json")

    context = {
        "bikes": bikes,
        "stations": stations,
    }

    return render(request, "web_bikes/bike_list.html", context)


def bike_detail_view(request, bike_id):
    """Показать подробную информацию о велосипеде."""
    bikes = load_bikes("data/bikes.json")
    bike = get_bike_by_id(bikes, bike_id)

    context = {
        "bike": bike,
    }

    return render(
        request,
        "web_bikes/bike_detail.html",
        context,
        status=404 if bike is None else 200,
    )
