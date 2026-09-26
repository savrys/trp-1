import datetime
from models import (
    show_bikes, show_stations, show_users,
    show_rentals, create_rental
)
from storage import (
    load_bikes, save_bikes,
    load_stations, save_stations,
    load_users, save_users,
    load_rentals, save_rentals
)

BIKES_FILE = "data/bikes.json"
STATIONS_FILE = "data/stations.json"
USERS_FILE = "data/users.json"
RENTALS_FILE = "data/rentals.json"


def main() -> None:
    bikes = load_bikes(BIKES_FILE)
    stations = load_stations(STATIONS_FILE)
    users = load_users(USERS_FILE)
    rentals = load_rentals(RENTALS_FILE, bikes, users, stations)

    while True:
        print("\n=== СИСТЕМА ПРОКАТА ВЕЛОСИПЕДОВ (ООП) ===")
        print("1. Показать велосипеды")
        print("2. Показать станции")
        print("3. Показать пользователей")
        print("4. Показать историю проката")
        print("5. Оформить аренду велосипеда")
        print("6. Завершить активную аренду")
        print("0. Сохранить изменения и выйти")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_bikes(bikes)
        elif choice == "2":
            show_stations(stations)
        elif choice == "3":
            show_users(users)
        elif choice == "4":
            show_rentals(rentals)
        elif choice == "5":
            if not users or not bikes or not stations:
                print("Ошибка: база данных сущностей пуста.")
                continue

            try:
                u_id = int(input("Введите ID пользователя: "))
                b_id = int(input("Введите ID велосипеда: "))
                s_id = int(input("Введите ID станции: "))

                user = next((u for u in users if u.id == u_id), None)
                bike = next((b for b in bikes if b.id == b_id), None)
                station = next((s for s in stations if s.id == s_id), None)

                if not user or not bike or not station:
                    print("Ошибка: ID не найдены.")
                    continue

                r_id = len(rentals) + 1
                now_str = datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                new_rental = create_rental(
                    rentals, r_id, bike, user, station, now_str
                )
                if new_rental:
                    print(f"Успех! Создан прокат:\n{new_rental}")
            except ValueError:
                print("Ошибка: Введен некорректный числовой ID.")

        elif choice == "6":
            try:
                r_id = int(input("Введите ID проката для завершения: "))
                rental = next(
                    (r for r in rentals
                     if r.id == r_id and not r.is_completed),
                    None
                )
                if rental:
                    rental.complete_rental()
                    print(f"Аренда #{r_id} завершена успешно.")
                else:
                    print("Ошибка: Активный прокат с таким ID не найден.")
            except ValueError:
                print("Ошибка ввода цифровых данных.")

        elif choice == "0":
            save_bikes(bikes, BIKES_FILE)
            save_stations(stations, STATIONS_FILE)
            save_users(users, USERS_FILE)
            save_rentals(rentals, RENTALS_FILE)
            print("Все данные успешно сохранены. До свидания!")
            break
        else:
            print("Некорректный выбор меню. Попробуйте еще раз.")


if __name__ == "__main__":
    main()
