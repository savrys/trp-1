"""Тесты для модуля stations."""

from stations import (
    add_station,
    count_bikes_at_station,
    find_station_by_id,
    find_stations_by_name,
)


def test_add_station():
    stations: list[dict] = []
    station = add_station(stations, "Центральная", "ул. Ленина, 1", 20)
    assert len(stations) == 1
    assert station["name"] == "Центральная"
    assert station["capacity"] == 20


def test_find_station_by_id():
    stations: list[dict] = []
    add_station(stations, "Центральная", "ул. Ленина, 1", 20)
    assert find_station_by_id(stations, 1)["name"] == "Центральная"
    assert find_station_by_id(stations, 99) is None


def test_find_stations_by_name():
    stations: list[dict] = []
    add_station(stations, "Центральная", "ул. Ленина, 1", 20)
    add_station(stations, "Парковая", "ул. Садовая, 5", 15)
    found = find_stations_by_name(stations, "парк")
    assert len(found) == 1


def test_count_bikes_at_station():
    stations: list[dict] = []
    add_station(stations, "Центральная", "ул. Ленина, 1", 20)
    bikes = [
        {"id": 1, "station_id": 1},
        {"id": 2, "station_id": 1},
        {"id": 3, "station_id": 2},
    ]
    assert count_bikes_at_station(bikes, 1) == 2
    assert count_bikes_at_station(bikes, 2) == 1