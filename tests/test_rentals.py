from models import Bike, User, Station, Rental, create_rental


def test_rental_object_interconnection():
    bike = Bike(1, "Giant Escape", "Hybrid")
    user = User(1, "Алексей", "alex@mail.ru")
    station = Station(1, "Парк Горького", 15)

    rental = Rental(101, bike, user, station, "2026-09-26 12:00:00")

    assert rental.bike is bike
    assert rental.user is user
    assert rental.station is station
    assert rental.is_completed is False


def test_create_rental_business_logic():
    rentals_list = []
    bike = Bike(2, "Scott Aspect", "Mountain", is_available=True)
    user = User(2, "Мария", "maria@yandex.ru")
    station = Station(2, "ВДНХ", 20)

    successful_rental = create_rental(
        rentals_list, 1, bike, user, station, "2026-09-26 13:00:00"
    )

    assert successful_rental is not None
    assert len(rentals_list) == 1
    assert bike.is_available is False

    failed_rental = create_rental(
        rentals_list, 2, bike, user, station, "2026-09-26 13:05:00"
    )
    assert failed_rental is None
    assert len(rentals_list) == 1


def test_complete_rental_workflow():
    bike = Bike(3, "Merida Big.Seven", "Mountain", is_available=False)
    user = User(3, "Петр", "petr@gmail.com")
    station = Station(3, "Сокольники", 30)
    rental = Rental(
        5, bike, user, station, "2026-09-26 10:00:00", is_completed=False
    )

    rental.complete_rental()
    assert rental.is_completed is True
    assert bike.is_available is True
