"""Сохранение и загрузка данных проекта в JSON-файлах."""

import json
import os


def load_json(filename: str, default: list | dict) -> list | dict:
    """Загрузить данные из JSON-файла."""
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Ошибка загрузки {filename}: {e}")
        return default


def save_json(filename: str, data: list | dict) -> None:
    """Сохранить данные в JSON-файл."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Ошибка сохранения {filename}: {e}")


def load_data(data_type: str) -> list:
    """Загрузить данные указанного типа."""
    return load_json(f"data/{data_type}.json", [])


def save_data(data_type: str, data: list) -> None:
    """Сохранить данные указанного типа."""
    save_json(f"data/{data_type}.json", data)