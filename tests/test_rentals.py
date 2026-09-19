"""Тесты для модуля rentals."""

from datetime import datetime

from rentals import (
    calculate_discount,
    calculate_total,
    cancel_rental,
    complete_rental,
    create_rental,
    find_rentals_by_user,
    get_active_rentals,
    get_total_revenue,
)


def test_calculate_discount():
    assert calculate_discount(3) == 0.0
    assert calculate_discount(5) == 0.10
    assert calculate_discount(10) == 0.20


def test_calculate_total():
    result = calculate_total(10, 200)
    assert result["base_cost"] == 2000
    assert result["discount"] == 0.20
    assert result["total"] == 1600


def test_create_rental():
    rentals: list[dict] = []
    rental = create_rental(
        rentals, bike_id=1, user_id=1, station_id=1, hours=5,
        start_time=datetime(2026, 9, 15, 10, 0)
    )
    assert len(rentals) == 1
    assert rental["status"] == "active"
    assert rental["hours"] == 5
    assert rental["total"] == 900  # городской: 200*5 - 10%


def test_complete_rental():
    rentals: list[dict] = []
    create_rental(rentals, 1, 1, 1, 2)
    assert complete_rental(rentals, 1) is True
    assert rentals[0]["status"] == "completed"
    assert complete_rental(rentals, 99) is False


def test_cancel_rental():
    rentals: list[dict] = []
    create_rental(rentals, 1, 1, 1, 2)
    assert cancel_rental(rentals, 1) is True
    assert len(rentals) == 0
    assert cancel_rental(rentals, 99) is False


def test_find_rentals_by_user():
    rentals: list[dict] = []
    create_rental(rentals, 1, 1, 1, 2)
    create_rental(rentals, 2, 2, 1, 3)
    found = find_rentals_by_user(rentals, 1)
    assert len(found) == 1
    assert found[0]["user_id"] == 1


def test_get_active_rentals():
    rentals: list[dict] = []
    create_rental(rentals, 1, 1, 1, 2)
    create_rental(rentals, 2, 2, 1, 3)
    complete_rental(rentals, 1)
    assert len(get_active_rentals(rentals)) == 1


def test_get_total_revenue():
    rentals: list[dict] = []
    create_rental(rentals, 1, 1, 1, 2)  # 400
    create_rental(rentals, 2, 2, 1, 2)  # 600
    assert get_total_revenue(rentals) == 1000