"""Тесты для модуля bikes."""

from bikes import (
    add_bike,
    get_available_bikes,
    get_bike_name,
    get_bike_price,
    sort_bikes_by_price,
)


def test_get_bike_price():
    assert get_bike_price("1") == 200
    assert get_bike_price("2") == 300
    assert get_bike_price("3") == 150
    assert get_bike_price("99") == 0


def test_get_bike_name():
    assert get_bike_name("1") == "городской"
    assert get_bike_name("99") == "неизвестный"


def test_add_bike():
    bikes: list[dict] = []
    bike = add_bike(bikes, "2", 1, "SN-001")
    assert len(bikes) == 1
    assert bike["name"] == "горный"
    assert bike["status"] == "available"
    assert bike["station_id"] == 1


def test_get_available_bikes():
    bikes: list[dict] = []
    add_bike(bikes, "1", 1, "SN-001")
    add_bike(bikes, "2", 1, "SN-002")
    bikes[1]["status"] = "rented"
    available = get_available_bikes(bikes)
    assert len(available) == 1
    assert available[0]["id"] == 1


def test_sort_bikes_by_price():
    bikes: list[dict] = []
    add_bike(bikes, "2", 1, "SN-001")  # 300
    add_bike(bikes, "1", 1, "SN-002")  # 200
    add_bike(bikes, "3", 1, "SN-003")  # 150
    sorted_bikes = sort_bikes_by_price(bikes)
    assert sorted_bikes[0]["price_per_hour"] == 150
    assert sorted_bikes[-1]["price_per_hour"] == 300