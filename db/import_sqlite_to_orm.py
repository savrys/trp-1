"""Перенос данных из SQLite-базы ПР7 в базу Django ORM (ПР9).

Скрипт читает таблицы bikes, users, stations, rentals из
data/bikely.sqlite и сохраняет их через ORM, сохраняя исходные id.

Запуск (после python manage.py migrate):
    python db/import_sqlite_to_orm.py
"""

import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import django
from django.db import transaction
from django.utils import timezone

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bikely.settings")
django.setup()

from web_bikes.models import Bike, Station  # noqa: E402
from web_rentals.models import Rental, User  # noqa: E402

SOURCE_DB = BASE_DIR / "data" / "bikely.sqlite"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

TABLES = ("bikes", "users", "stations", "rentals")


def read_legacy_rows():
    """Прочитать все записи из базы предыдущей практической работы."""
    if not SOURCE_DB.exists():
        raise FileNotFoundError(
            f"Не найдена база-источник: {SOURCE_DB}"
        )

    connection = sqlite3.connect(SOURCE_DB)
    connection.row_factory = sqlite3.Row

    try:
        rows = {
            table: connection.execute(
                f"SELECT * FROM {table} ORDER BY id"
            ).fetchall()
            for table in TABLES
        }
    finally:
        connection.close()

    return rows


def parse_start_time(value):
    """Преобразовать строку времени из SQLite в aware datetime."""
    parsed = datetime.strptime(value, DATE_FORMAT)
    return timezone.make_aware(parsed)


def import_data():
    """Скопировать данные из SQLite в модели Django ORM."""
    rows = read_legacy_rows()

    with transaction.atomic():
        for row in rows["stations"]:
            Station.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "capacity": row["capacity"],
                },
            )

        for row in rows["bikes"]:
            Bike.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "model": row["model"],
                    "type": row["type"],
                    "is_available": bool(row["is_available"]),
                },
            )

        for row in rows["users"]:
            User.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "email": row["email"],
                },
            )

        for row in rows["rentals"]:
            Rental.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "bike_id": row["bike_id"],
                    "user_id": row["user_id"],
                    "station_id": row["station_id"],
                    "start_time": parse_start_time(row["start_time"]),
                    "is_completed": bool(row["is_completed"]),
                },
            )

    print("Перенос данных в Django ORM завершён.")
    print(f"Станций: {Station.objects.count()}")
    print(f"Велосипедов: {Bike.objects.count()}")
    print(f"Клиентов: {User.objects.count()}")
    print(f"Аренд: {Rental.objects.count()}")


if __name__ == "__main__":
    import_data()
