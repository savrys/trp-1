"""Консольное приложение для аренды велосипедов."""

from bikes import (
    BIKE_TYPES,
    add_bike,
    get_available_bikes,
    get_bike_name,
    get_bike_price,
    sort_bikes_by_price,
)
from rentals import (
    cancel_rental,
    complete_rental,
    create_rental,
    find_rentals_by_user,
    get_active_rentals,
    get_popular_bike_type,
    get_total_revenue,
    sort_rentals_by_total,
)
from stations import (
    add_station,
    count_bikes_at_station,
    find_station_by_id,
    find_stations_by_name,
)
from storage import load_data, save_data
from users import add_user, find_user_by_id, find_users_by_name
from utils import input_int, input_non_empty

# Файлы данных
BIKES_FILE = "bikes"
USERS_FILE = "users"
STATIONS_FILE = "stations"
RENTALS_FILE = "rentals"


def show_menu() -> None:
    """Вывести главное меню."""
    print()
    print("=" * 45)
    print("   Аренда велосипедов")
    print("=" * 45)
    print("1. Показать типы велосипедов")
    print("2. Показать станции")
    print("3. Показать доступные велосипеды")
    print("4. Зарегистрировать пользователя")
    print("5. Оформить аренду")
    print("6. Завершить аренду")
    print("7. Показать активные аренды")
    print("8. Найти аренды пользователя")
    print("9. Показать статистику")
    print("10. Добавить велосипед")
    print("11. Добавить станцию")
    print("0. Выход")


def show_bike_types() -> None:
    """Вывести доступные типы велосипедов."""
    print()
    print("Доступные типы велосипедов:")
    for key, bike in BIKE_TYPES.items():
        print(f"  {key} - {bike['name']:10s} ({bike['price']} руб/час)")


def show_stations(stations: list[dict]) -> None:
    """Вывести список станций."""
    if not stations:
        print("Станций пока нет.")
        return
    print()
    print(f"{'ID':<4}{'Название':<20}{'Адрес':<30}{'Вместимость':<12}")
    print("-" * 70)
    for s in stations:
        print(f"{s['id']:<4}{s['name']:<20}{s['address']:<30}{s['capacity']:<12}")


def show_bikes(bikes: list[dict]) -> None:
    """Вывести список велосипедов."""
    if not bikes:
        print("Велосипедов пока нет.")
        return
    print()
    print(f"{'ID':<4}{'Тип':<12}{'Цена':<8}{'Станция':<10}{'Статус':<12}")
    print("-" * 50)
    for b in bikes:
        print(
            f"{b['id']:<4}{b['name']:<12}{b['price_per_hour']:<8}"
            f"{b['station_id']:<10}{b['status']:<12}"
        )


def show_rentals(rentals: list[dict]) -> None:
    """Вывести список аренд."""
    if not rentals:
        print("Аренд пока нет.")
        return
    print()
    print(f"{'ID':<4}{'Велосипед':<6}{'Пользователь':<14}{'Часы':<6}{'Итого':<10}{'Статус':<10}")
    print("-" * 60)
    for r in rentals:
        print(
            f"{r['id']:<4}{r['bike_id']:<6}{r['user_id']:<14}"
            f"{r['hours']:<6}{r['total']:<10.0f}{r['status']:<10}"
        )


def handle_add_station(stations: list[dict]) -> None:
    """Добавить станцию."""
    name = input_non_empty("Название станции: ")
    address = input_non_empty("Адрес: ")
    capacity = input_int("Вместимость: ")
    station = add_station(stations, name, address, capacity)
    save_data(STATIONS_FILE, stations)
    print(f"Станция #{station['id']} добавлена.")


def handle_add_bike(bikes: list[dict], stations: list[dict]) -> None:
    """Добавить велосипед."""
    show_bike_types()
    bike_type = input("Введите тип велосипеда (1/2/3): ").strip()
    if bike_type not in BIKE_TYPES:
        print("Ошибка: неизвестный тип.")
        return
    show_stations(stations)
    station_id = input_int("ID станции: ")
    if not find_station_by_id(stations, station_id):
        print("Ошибка: станция не найдена.")
        return
    serial = input_non_empty("Серийный номер: ")
    bike = add_bike(bikes, bike_type, station_id, serial)
    save_data(BIKES_FILE, bikes)
    print(f"Велосипед #{bike['id']} ({bike['name']}) добавлен на станцию {station_id}.")


def handle_register_user(users: list[dict]) -> None:
    """Зарегистрировать пользователя."""
    name = input_non_empty("Имя пользователя: ")
    phone = input_non_empty("Телефон: ")
    user = add_user(users, name, phone)
    save_data(USERS_FILE, users)
    print(f"Пользователь #{user['id']} зарегистрирован.")


def handle_create_rental(
    rentals: list[dict],
    bikes: list[dict],
    users: list[dict],
    stations: list[dict],
) -> None:
    """Оформить аренду."""
    available = get_available_bikes(bikes)
    if not available:
        print("Нет доступных велосипедов.")
        return
    show_bikes(available)
    bike_id = input_int("ID велосипеда: ")
    bike = next((b for b in available if b["id"] == bike_id), None)
    if not bike:
        print("Ошибка: велосипед недоступен.")
        return

    user_id = input_int("ID пользователя: ")
    if not find_user_by_id(users, user_id):
        print("Ошибка: пользователь не найден.")
        return

    hours = input_int("Количество часов: ")
    if hours <= 0:
        print("Ошибка: количество часов должно быть положительным.")
        return

    rental = create_rental(
        rentals, bike_id, user_id, bike["station_id"], hours
    )
    # Помечаем велосипед как арендованный
    bike["status"] = "rented"
    save_data(RENTALS_FILE, rentals)
    save_data(BIKES_FILE, bikes)

    print()
    print(f"Аренда #{rental['id']} оформлена.")
    print(f"Велосипед:    {bike['name']}")
    print(f"Пользователь: {find_user_by_id(users, user_id)['name']}")
    print(f"Часы:         {rental['hours']}")
    print(f"Начало:       {rental['start_time']}")
    print(f"Окончание:    {rental['end_time']}")
    print(f"Скидка:       {int(rental['discount'] * 100)}%")
    print(f"ИТОГО:        {rental['total']:.0f} руб.")


def handle_complete_rental(rentals: list[dict], bikes: list[dict]) -> None:
    """Завершить аренду."""
    active = get_active_rentals(rentals)
    if not active:
        print("Нет активных аренд.")
        return
    show_rentals(active)
    rental_id = input_int("ID аренды для завершения: ")
    rental = next((r for r in active if r["id"] == rental_id), None)
    if not rental:
        print("Аренда не найдена.")
        return
    complete_rental(rentals, rental_id)
    # Возвращаем велосипед в доступные
    bike = next((b for b in bikes if b["id"] == rental["bike_id"]), None)
    if bike:
        bike["status"] = "available"
    save_data(RENTALS_FILE, rentals)
    save_data(BIKES_FILE, bikes)
    print(f"Аренда #{rental_id} завершена.")


def handle_find_user_rentals(rentals: list[dict], users: list[dict]) -> None:
    """Найти аренды пользователя."""
    query = input_non_empty("Имя пользователя (или часть): ")
    found_users = find_users_by_name(users, query)
    if not found_users:
        print("Пользователи не найдены.")
        return
    for u in found_users:
        user_rentals = find_rentals_by_user(rentals, u["id"])
        print(f"\nПользователь: {u['name']} (ID {u['id']})")
        if user_rentals:
            show_rentals(user_rentals)
        else:
            print("  Аренд нет.")


def handle_statistics(rentals: list[dict], bikes: list[dict]) -> None:
    """Показать статистику."""
    if not rentals:
        print("Нет данных для статистики.")
        return
    print()
    print(f"Всего аренд:          {len(rentals)}")
    print(f"Активных аренд:       {len(get_active_rentals(rentals))}")
    print(f"Общая выручка:        {get_total_revenue(rentals):.0f} руб.")
    print(f"Самый популярный тип: {get_popular_bike_type(rentals, bikes)}")
    print()
    print("Топ-3 по стоимости:")
    top = sort_rentals_by_total(rentals)[:3]
    for i, r in enumerate(top, 1):
        print(f"  {i}. Аренда #{r['id']} — {r['total']:.0f} руб.")


def main() -> None:
    """Точка запуска приложения."""
    bikes = load_data(BIKES_FILE)
    users = load_data(USERS_FILE)
    stations = load_data(STATIONS_FILE)
    rentals = load_data(RENTALS_FILE)

    while True:
        show_menu()
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            show_bike_types()
        elif choice == "2":
            show_stations(stations)
        elif choice == "3":
            show_bikes(get_available_bikes(bikes))
        elif choice == "4":
            handle_register_user(users)
        elif choice == "5":
            handle_create_rental(rentals, bikes, users, stations)
        elif choice == "6":
            handle_complete_rental(rentals, bikes)
        elif choice == "7":
            show_rentals(get_active_rentals(rentals))
        elif choice == "8":
            handle_find_user_rentals(rentals, users)
        elif choice == "9":
            handle_statistics(rentals, bikes)
        elif choice == "10":
            handle_add_bike(bikes, stations)
        elif choice == "11":
            handle_add_station(stations)
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("Неизвестная команда.")


if __name__ == "__main__":
    main()