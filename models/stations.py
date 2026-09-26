from typing import List


class Station:
    """Класс, описывающий станцию проката."""

    def __init__(self, station_id: int, name: str, capacity: int) -> None:
        self.id: int = station_id
        self.name: str = name
        self.capacity: int = capacity

    def has_free_slots(self, current_bikes_count: int) -> bool:
        """Проверяет, есть ли свободные места на станции для парковки."""
        return self.capacity > current_bikes_count

    def __str__(self) -> str:
        return (
            f"Станция '{self.name}' (ID: {self.id}, "
            f"Вместимость: {self.capacity} мест)"
        )


def add_station(stations: List[Station], station_id: int,
                name: str, capacity: int) -> Station:
    """Создает объект Station и добавляет его в коллекцию."""
    new_station = Station(station_id, name, capacity)
    stations.append(new_station)
    return new_station


def show_stations(stations: List[Station]) -> None:
    """Выводит список станций."""
    if not stations:
        print("Список станций пуст.")
        return
    for station in stations:
        print(station)
