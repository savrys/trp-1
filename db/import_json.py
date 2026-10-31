import json
from pathlib import Path

from db.database import get_connection
from db.init_db import initialize_database


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename):
    """Загрузить данные из JSON-файла."""
    file_path = DATA_DIR / filename

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def import_json_data():
    """Перенести данные из JSON-файлов в SQLite."""
    initialize_database()

    bikes = load_json("bikes.json")
    users = load_json("users.json")
    stations = load_json("stations.json")
    rentals = load_json("rentals.json")

    connection = get_connection()

    try:
        connection.execute("DELETE FROM rentals")
        connection.execute("DELETE FROM bikes")
        connection.execute("DELETE FROM users")
        connection.execute("DELETE FROM stations")

        connection.executemany(
            """
            INSERT INTO bikes (id, model, type, is_available)
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    bike["id"],
                    bike["model"],
                    bike["type"],
                    int(bike["is_available"]),
                )
                for bike in bikes
            ],
        )

        connection.executemany(
            """
            INSERT INTO users (id, name, email)
            VALUES (?, ?, ?)
            """,
            [
                (user["id"], user["name"], user["email"])
                for user in users
            ],
        )

        connection.executemany(
            """
            INSERT INTO stations (id, name, capacity)
            VALUES (?, ?, ?)
            """,
            [
                (station["id"], station["name"], station["capacity"])
                for station in stations
            ],
        )

        connection.executemany(
            """
            INSERT INTO rentals (
                id, bike_id, user_id, station_id, start_time, is_completed
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    rental["id"],
                    rental["bike_id"],
                    rental["user_id"],
                    rental["station_id"],
                    rental["start_time"],
                    int(rental["is_completed"]),
                )
                for rental in rentals
            ],
        )

        connection.commit()

        print("Импорт JSON завершён.")
        print(f"Велосипедов: {len(bikes)}")
        print(f"Пользователей: {len(users)}")
        print(f"Станций: {len(stations)}")
        print(f"Аренд: {len(rentals)}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    import_json_data()