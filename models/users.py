from typing import List


class User:
    """Класс, описывающий пользователя системы проката."""

    def __init__(self, user_id: int, name: str, email: str) -> None:
        self.id: int = user_id
        self.name: str = name
        self.email: str = email

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создает объект пользователя из словаря."""
        return cls(
            user_id=data["id"],
            name=data["name"],
            email=data["email"]
        )

    def __str__(self) -> str:
        return f"Клиент #{self.id}: {self.name} ({self.email})"


def add_user(users: List[User], user_id: int,
             name: str, email: str) -> User:
    """Создает объект User и добавляет его в коллекцию."""
    new_user = User(user_id, name, email)
    users.append(new_user)
    return new_user


def show_users(users: List[User]) -> None:
    """Выводит список пользователей."""
    if not users:
        print("Список пользователей пуст.")
        return
    for user in users:
        print(user)
