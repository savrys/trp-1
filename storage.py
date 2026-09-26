import json
import os
from typing import List
from models import Bike, Station, User, Rental


def ensure_dir(filepath: str) -> None:
    dirname = os.path.dirname(filepath)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)


def load_bikes(filepath: str) -> List[Bike]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [
        Bike(i["id"], i["model"], i["type"], i["is_available"])
        for i in data
    ]


def save_bikes(bikes: List[Bike], filepath: str) -> None:
    ensure_dir(filepath)
    data = [
        {
            "id": b.id,
            "model": b.model,
            "type": b.type,
            "is_available": b.is_available
        }
        for b in bikes
    ]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_stations(filepath: str) -> List[Station]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [Station(i["id"], i["name"], i["capacity"]) for i in data]


def save_stations(stations: List[Station], filepath: str) -> None:
    ensure_dir(filepath)
    data = [
        {"id": s.id, "name": s.name, "capacity": s.capacity}
        for s in stations
    ]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_users(filepath: str) -> List[User]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [User.from_data(item) for item in data]


def save_users(users: List[User], filepath: str) -> None:
    ensure_dir(filepath)
    data = [{"id": u.id, "name": u.name, "email": u.email} for u in users]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_rentals(filepath: str, bikes: List[Bike], users: List[User],
                 stations: List[Station]) -> List[Rental]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        data_list = json.load(f)

    rentals = []
    for item in data_list:
        bike = next((b for b in bikes if b.id == item["bike_id"]), None)
        user = next((u for u in users if u.id == item["user_id"]), None)
        station = next((s for s in stations if s.id == item["station_id"]),
                       None)

        if bike and user and station:
            rental = Rental(
                rental_id=item["id"],
                bike=bike,
                user=user,
                station=station,
                start_time=item["start_time"],
                is_completed=item["is_completed"]
            )
            rentals.append(rental)
    return rentals


def save_rentals(rentals: List[Rental], filepath: str) -> None:
    ensure_dir(filepath)
    data = [
        {
            "id": r.id,
            "bike_id": r.bike.id,  # Извлекаем ID живого объекта
            "user_id": r.user.id,
            "station_id": r.station.id,
            "start_time": r.start_time,
            "is_completed": r.is_completed
        }
        for r in rentals
    ]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
