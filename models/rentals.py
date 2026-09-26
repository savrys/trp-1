from typing import List, Optional
from .bikes import Bike
from .users import User
from .stations import Station


class Rental:
    """Класс, описывающий процесс аренды велосипеда."""

    def __init__(self, rental_id: int, bike: Bike, user: User,
                 station: Station, start_time: str,
                 is_completed: bool = False) -> None:
        self.id: int = rental_id
        self.bike: Bike = bike
        self.user: User = user
        self.station: Station = station
        self.start_time: str = start_time
        self.is_completed: bool = is_completed

    def complete_rental(self) -> None:
        """Завершает аренду и делает велосипед снова доступным."""
        self.is_completed = True
        self.bike.change_availability(True)

    def __str__(self) -> str:
        status = "Завершена" if self.is_completed else "Активна"
        return (
            f"Аренда #{self.id} | Пользователь: {self.user.name} | "
            f"Велосипед: {self.bike.model} | "
            f"Станция: {self.station.name} | Статус: {status}"
        )


def is_bike_rented(rentals: List[Rental], bike_id: int) -> bool:
    """Проверяет, находится ли велосипед в активной аренде."""
    for rental in rentals:
        if rental.bike.id == bike_id and not rental.is_completed:
            return True
    return False


def create_rental(rentals: List[Rental], rental_id: int, bike: Bike,
                  user: User, station: Station,
                  start_time: str) -> Optional[Rental]:
    """Создает аренду, связывая объекты между собой."""
    if not bike.is_available:
        print(f"Ошибка: Велосипед #{bike.id} уже занят!")
        return None

    new_rental = Rental(rental_id, bike, user, station, start_time)
    bike.change_availability(False)
    rentals.append(new_rental)
    return new_rental


def show_rentals(rentals: List[Rental]) -> None:
    """Выводит историю проката."""
    if not rentals:
        print("История проката пуста.")
        return
    for rental in rentals:
        print(rental)
