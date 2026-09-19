"""Функции для работы со станциями."""


def add_station(stations: list[dict], name: str, address: str, capacity: int) -> dict:
    """Добавить станцию в список.

    Возвращает словарь станции.
    """
    station = {
        "id": len(stations) + 1,
        "name": name,
        "address": address,
        "capacity": capacity,
    }
    stations.append(station)
    return station


def find_station_by_id(stations: list[dict], station_id: int) -> dict | None:
    """Найти станцию по ID."""
    for s in stations:
        if s["id"] == station_id:
            return s
    return None


def find_stations_by_name(stations: list[dict], query: str) -> list[dict]:
    """Найти станции по подстроке названия."""
    query_lower = query.lower()
    return [s for s in stations if query_lower in s["name"].lower()]


def count_bikes_at_station(bikes: list[dict], station_id: int) -> int:
    """Посчитать количество велосипедов на станции."""
    return sum(1 for b in bikes if b["station_id"] == station_id)