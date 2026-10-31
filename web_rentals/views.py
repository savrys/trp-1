from django.shortcuts import render

from db.repository import get_rentals_for_views

from models.bikes import Bike
from models.users import User
from models.stations import Station
from models.rentals import Rental


def get_all_rentals():
    """Получить аренды из SQLite и создать связанные объекты."""
    rows = get_rentals_for_views()
    rentals = []

    for row in rows:
        bike = Bike(
            bike_id=row["bike_id"],
            model=row["bike_model"],
            type_bike=row["bike_type"],
            is_available=bool(row["bike_is_available"]),
        )

        user = User(
            user_id=row["user_id"],
            name=row["user_name"],
            email=row["user_email"],
        )

        station = Station(
            station_id=row["station_id"],
            name=row["station_name"],
            capacity=row["station_capacity"],
        )

        rental = Rental(
            rental_id=row["rental_id"],
            bike=bike,
            user=user,
            station=station,
            start_time=row["start_time"],
            is_completed=bool(row["is_completed"]),
        )

        rentals.append(rental)

    return rentals


def get_rental_by_id(rentals_list, rental_id):
    """Найти аренду по идентификатору."""
    for rental in rentals_list:
        if rental.id == rental_id:
            return rental
    return None


def rentals_list_view(request):
    """Страница со списком аренд."""
    rentals = get_all_rentals()

    return render(
        request,
        "web_rentals/rental_list.html",
        {"rentals": rentals},
    )


def rental_detail_view(request, rental_id):
    """Страница с подробной информацией об аренде."""
    rentals = get_all_rentals()
    rental = get_rental_by_id(rentals, rental_id)

    return render(
        request,
        "web_rentals/rental_detail.html",
        {"rental": rental},
        status=404 if rental is None else 200,
    )