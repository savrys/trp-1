from db.database import get_connection


def get_all_bikes():
    """Получить список всех велосипедов."""
    connection = get_connection()
    try:
        return connection.execute(
            "SELECT * FROM bikes ORDER BY id"
        ).fetchall()
    finally:
        connection.close()


def get_available_bikes():
    """Получить доступные велосипеды."""
    connection = get_connection()
    try:
        return connection.execute(
            """
            SELECT *
            FROM bikes
            WHERE is_available = 1
            ORDER BY id
            """
        ).fetchall()
    finally:
        connection.close()


def get_bike_by_id(bike_id):
    """Получить велосипед по идентификатору."""
    connection = get_connection()
    try:
        return connection.execute(
            "SELECT * FROM bikes WHERE id = ?",
            (bike_id,),
        ).fetchone()
    finally:
        connection.close()


def get_all_stations():
    """Получить все станции."""
    connection = get_connection()
    try:
        return connection.execute(
            "SELECT * FROM stations ORDER BY id"
        ).fetchall()
    finally:
        connection.close()


def get_all_rentals():
    """Получить аренды с названиями связанных объектов."""
    connection = get_connection()
    try:
        return connection.execute(
            """
            SELECT
                rentals.id AS rental_id,
                bikes.model AS bike_model,
                users.name AS user_name,
                stations.name AS station_name,
                rentals.start_time,
                rentals.is_completed
            FROM rentals
            JOIN bikes ON rentals.bike_id = bikes.id
            JOIN users ON rentals.user_id = users.id
            JOIN stations ON rentals.station_id = stations.id
            ORDER BY rentals.id
            """
        ).fetchall()
    finally:
        connection.close()


def get_rentals_for_views():
    """Получить аренды со всеми данными для Django-шаблонов."""
    connection = get_connection()
    try:
        return connection.execute(
            """
            SELECT
                rentals.id AS rental_id,
                rentals.start_time,
                rentals.is_completed,

                bikes.id AS bike_id,
                bikes.model AS bike_model,
                bikes.type AS bike_type,
                bikes.is_available AS bike_is_available,

                users.id AS user_id,
                users.name AS user_name,
                users.email AS user_email,

                stations.id AS station_id,
                stations.name AS station_name,
                stations.capacity AS station_capacity

            FROM rentals
            JOIN bikes ON rentals.bike_id = bikes.id
            JOIN users ON rentals.user_id = users.id
            JOIN stations ON rentals.station_id = stations.id
            ORDER BY rentals.id
            """
        ).fetchall()
    finally:
        connection.close()


def get_active_rentals():
    """Получить незавершённые аренды."""
    connection = get_connection()
    try:
        return connection.execute(
            """
            SELECT *
            FROM rentals
            WHERE is_completed = 0
            ORDER BY id
            """
        ).fetchall()
    finally:
        connection.close()


def get_bike_counts_by_type():
    """Посчитать велосипеды каждого типа."""
    connection = get_connection()
    try:
        return connection.execute(
            """
            SELECT type, COUNT(*) AS bike_count
            FROM bikes
            GROUP BY type
            """
        ).fetchall()
    finally:
        connection.close()


def get_rental_counts_by_user():
    """Посчитать количество аренд каждого пользователя."""
    connection = get_connection()
    try:
        return connection.execute(
            """
            SELECT
                users.name,
                COUNT(rentals.id) AS rental_count
            FROM users
            LEFT JOIN rentals ON users.id = rentals.user_id
            GROUP BY users.id, users.name
            """
        ).fetchall()
    finally:
        connection.close()