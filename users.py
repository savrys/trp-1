"""Функции для работы с пользователями."""

from datetime import datetime


def add_user(users: list[dict], name: str, phone: str) -> dict:
    """Добавить пользователя в список.

    Возвращает словарь пользователя.
    """
    user = {
        "id": len(users) + 1,
        "name": name,
        "phone": phone,
        "registration_date": datetime.now().strftime("%d.%m.%Y"),
    }
    users.append(user)
    return user


def find_user_by_id(users: list[dict], user_id: int) -> dict | None:
    """Найти пользователя по ID."""
    for u in users:
        if u["id"] == user_id:
            return u
    return None


def find_users_by_name(users: list[dict], query: str) -> list[dict]:
    """Найти пользователей по подстроке имени."""
    query_lower = query.lower()
    return [u for u in users if query_lower in u["name"].lower()]


def find_user_by_phone(users: list[dict], phone: str) -> dict | None:
    """Найти пользователя по номеру телефона."""
    for u in users:
        if u["phone"] == phone:
            return u
    return None