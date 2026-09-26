from typing import List


class Bike:
    """Класс, описывающий велосипед в системе проката."""

    def __init__(self, bike_id: int, model: str,
                 type_bike: str, is_available: bool = True) -> None:
        self.id: int = bike_id
        self.model: str = model
        self.type: str = type_bike
        self.is_available: bool = is_available

    def change_availability(self, status: bool) -> None:
        """Изменить статус доступности велосипеда."""
        self.is_available = status

    def __str__(self) -> str:
        status = "Доступен" if self.is_available else "В прокате"
        return f"Велосипед #{self.id}: {self.model} ({self.type}) — [{status}]"


def add_bike(bikes: List[Bike], bike_id: int,
             model: str, type_bike: str) -> Bike:
    """Создает объект Bike и добавляет его в коллекцию."""
    new_bike = Bike(bike_id, model, type_bike)
    bikes.append(new_bike)
    return new_bike


def find_bike(bikes: List[Bike], query: str) -> List[Bike]:
    """Поиск велосипедов по модели или типу."""
    query = query.lower()
    return [b for b in bikes if query in b.model.lower()
            or query in b.type.lower()]


def show_bikes(bikes: List[Bike]) -> None:
    """Выводит список велосипедов в консоль."""
    if not bikes:
        print("Список велосипедов пуст.")
        return
    for bike in bikes:
        print(bike)
