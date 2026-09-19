"""Функции для работы с арендой."""

from datetime import datetime, timedelta

from bikes import get_bike_name, get_bike_price


def calculate_discount(hours: int) -> float:
    """Рассчитать скидку в зависимости от количества часов."""
    if hours >= 10:
        return 0.20
    elif hours >= 5:
        return 0.10
    return 0.0


def calculate_total(hours: int, price_per_hour: int) -> dict:
    """Рассчитать стоимость аренды и вернуть детализацию."""
    base_cost = price_per_hour * hours
    discount = calculate_discount(hours)
    discount_sum = base_cost * discount
    total = base_cost - discount_sum
    return {
        "base_cost": base_cost,
        "discount": discount,
        "discount_sum": discount_sum,
        "total": total,
    }


def create_rental(
    rentals: list[dict],
    bike_id: int,
    user_id: int,
    station_id: int,
    hours: int,
    start_time: datetime | None = None,
) -> dict:
    """Создать новую аренду.

    Возвращает словарь аренды.
    """
    if start_time is None:
        start_time = datetime.now()
    price_per_hour = get_bike_price(str(bike_id))  # условно
    cost = calculate_total(hours, price_per_hour)
    rental = {
        "id": len(rentals) + 1,
        "bike_id": bike_id,
        "user_id": user_id,
        "station_id": station_id,
        "hours": hours,
        "start_time": start_time.strftime("%d.%m.%Y %H:%M"),
        "end_time": (start_time + timedelta(hours=hours)).strftime("%d.%m.%Y %H:%M"),
        "base_cost": cost["base_cost"],
        "discount": cost["discount"],
        "discount_sum": cost["discount_sum"],
        "total": cost["total"],
        "status": "active",  # active / completed / cancelled
    }
    rentals.append(rental)
    return rental


def complete_rental(rentals: list[dict], rental_id: int) -> bool:
    """Завершить аренду по ID."""
    for r in rentals:
        if r["id"] == rental_id:
            r["status"] = "completed"
            return True
    return False


def cancel_rental(rentals: list[dict], rental_id: int) -> bool:
    """Отменить аренду по ID."""
    for i, r in enumerate(rentals):
        if r["id"] == rental_id:
            rentals.pop(i)
            return True
    return False


def find_rentals_by_user(rentals: list[dict], user_id: int) -> list[dict]:
    """Найти все аренды пользователя."""
    return [r for r in rentals if r["user_id"] == user_id]


def find_rentals_by_bike(rentals: list[dict], bike_id: int) -> list[dict]:
    """Найти все аренды велосипеда."""
    return [r for r in rentals if r["bike_id"] == bike_id]


def get_active_rentals(rentals: list[dict]) -> list[dict]:
    """Вернуть список активных аренд."""
    return [r for r in rentals if r["status"] == "active"]


def get_total_revenue(rentals: list[dict]) -> float:
    """Подсчитать общую выручку по всем арендам."""
    return sum(r["total"] for r in rentals)


def get_popular_bike_type(rentals: list[dict], bikes: list[dict]) -> str:
    """Вернуть самый популярный тип велосипеда."""
    if not rentals:
        return "нет данных"
    counts: dict[str, int] = {}
    for r in rentals:
        bike = next((b for b in bikes if b["id"] == r["bike_id"]), None)
        if bike:
            counts[bike["name"]] = counts.get(bike["name"], 0) + 1
    if not counts:
        return "нет данных"
    return max(counts, key=counts.get)


def sort_rentals_by_total(rentals: list[dict], reverse: bool = True) -> list[dict]:
    """Отсортировать аренды по итоговой стоимости."""
    return sorted(rentals, key=lambda r: r["total"], reverse=reverse)