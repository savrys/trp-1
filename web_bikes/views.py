from django.shortcuts import render

from db.repository import (
    get_all_bikes,
    get_all_stations,
    get_bike_by_id,
)

from models.bikes import Bike
from models.stations import Station


def bike_from_row(row):
    """Преобразовать запись SQLite в объект Bike."""
    if row is None:
        return None

    return Bike(
        bike_id=row["id"],
        model=row["model"],
        type_bike=row["type"],
        is_available=bool(row["is_available"]),
    )


def bikes_list_view(request):
    """Страница со списком велосипедов и станций."""
    bikes = [
        bike_from_row(row)
        for row in get_all_bikes()
    ]

    stations = [
        Station(
            station_id=row["id"],
            name=row["name"],
            capacity=row["capacity"],
        )
        for row in get_all_stations()
    ]

    context = {
        "bikes": bikes,
        "stations": stations,
    }

    return render(request, "web_bikes/bike_list.html", context)


def bike_detail_view(request, bike_id):
    """Страница с подробной информацией о велосипеде."""
    row = get_bike_by_id(bike_id)
    bike = bike_from_row(row)

    return render(
        request,
        "web_bikes/bike_detail.html",
        {"bike": bike},
        status=404 if bike is None else 200,
    )