from db.import_json import import_json_data
from db.repository import (
    get_all_bikes,
    get_available_bikes,
    get_all_rentals,
    get_bike_counts_by_type,
)


def main():
    print("=== Импорт данных ===")
    import_json_data()

    print("\n=== Все велосипеды ===")
    for bike in get_all_bikes():
        print(dict(bike))

    print("\n=== Доступные велосипеды ===")
    for bike in get_available_bikes():
        print(dict(bike))

    print("\n=== Аренды ===")
    for rental in get_all_rentals():
        print(dict(rental))

    print("\n=== Количество велосипедов по типам ===")
    for item in get_bike_counts_by_type():
        print(dict(item))


if __name__ == "__main__":
    main()