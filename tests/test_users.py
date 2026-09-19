"""Тесты для модуля users."""

from users import add_user, find_user_by_id, find_user_by_phone, find_users_by_name


def test_add_user():
    users: list[dict] = []
    user = add_user(users, "Иван", "+79001234567")
    assert len(users) == 1
    assert user["name"] == "Иван"
    assert user["phone"] == "+79001234567"


def test_find_user_by_id():
    users: list[dict] = []
    add_user(users, "Иван", "+79001234567")
    assert find_user_by_id(users, 1)["name"] == "Иван"
    assert find_user_by_id(users, 99) is None


def test_find_users_by_name():
    users: list[dict] = []
    add_user(users, "Иван Петров", "+79001234567")
    add_user(users, "Мария Сидорова", "+79007654321")
    found = find_users_by_name(users, "иван")
    assert len(found) == 1


def test_find_user_by_phone():
    users: list[dict] = []
    add_user(users, "Иван", "+79001234567")
    assert find_user_by_phone(users, "+79001234567")["name"] == "Иван"
    assert find_user_by_phone(users, "+70000000000") is None