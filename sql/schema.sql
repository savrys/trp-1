
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS bikes (
    id INTEGER PRIMARY KEY,
    model TEXT NOT NULL,
    type TEXT NOT NULL,
    is_available INTEGER NOT NULL DEFAULT 1
        CHECK (is_available IN (0, 1))
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS stations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity >= 0)
);

CREATE TABLE IF NOT EXISTS rentals (
    id INTEGER PRIMARY KEY,
    bike_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    station_id INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    is_completed INTEGER NOT NULL DEFAULT 0
        CHECK (is_completed IN (0, 1)),

    FOREIGN KEY (bike_id) REFERENCES bikes(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (station_id) REFERENCES stations(id)
);
