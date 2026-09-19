"""Функции для работы с велосипедами."""

# Словарь типов велосипедов
BIKE_TYPES: dict[str, dict] = {
    "1": {"name": "городской", "price": 200},
    "2": {"name": "горный", "price": 300},
    "3": {"name": "детский", "price": 150},
}


def get_bike_types() -> dict[str, dict]:
    """Вернуть словарь доступных типов велосипедов."""
    return BIKE_TYPES


def get_bike_price(bike_type: str) -> int:
    """Вернуть цену за час для указанного типа велосипеда."""
    bike = BIKE_TYPES.get(bike_type)
    return bike["price"] if bike else 0


def get_bike_name(bike_type: str) -> str:
    """Вернуть название типа велосипеда."""
    bike = BIKE_TYPES.get(bike_type)
    return bike["name"] if bike else "неизвестный"


def add_bike(
    bikes: list[dict],
    bike_type: str,
    station_id: int,
    serial_number: str,
) -> dict:
    """Добавить велосипед в список.

    Возвращает словарь велосипеда.
    """
    bike = {
        "id": len(bikes) + 1,
        "type": bike_type,
        "name": get_bike_name(bike_type),
        "price_per_hour": get_bike_price(bike_type),
        "station_id": station_id,
        "serial_number": serial_number,
        "status": "available",  # available / rented / maintenance
    }
    bikes.append(bike)
    return bike


def find_bike_by_id(bikes: list[dict], bike_id: int) -> dict | None:
    """Найти велосипед по ID."""
    for b in bikes:
        if b["id"] == bike_id:
            return b
    return None


def get_available_bikes(bikes: list[dict], station_id: int | None = None) -> list[dict]:
    """Вернуть список доступных велосипедов (опционально — на станции)."""
    return [
        b
        for b in bikes
        if b["status"] == "available"
        and (station_id is None or b["station_id"] == station_id)
    ]


def sort_bikes_by_price(bikes: list[dict], reverse: bool = False) -> list[dict]:
    """Отсортировать велосипеды по цене за час."""
    return sorted(bikes, key=lambda b: b["price_per_hour"], reverse=reverse)