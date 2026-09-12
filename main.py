import datetime

def get_bike_type() -> str:
    print("Доступные типы велосипедов:")
    print("  1 - городской (200 руб/час)")
    print("  2 - горный    (300 руб/час)")
    print("  3 - детский   (150 руб/час)")
    return input("Введите тип велосипеда (1/2/3): ").strip()

def get_hours() -> int:
    raw = input("На сколько часов арендуете велосипед? ").strip()
    return int(raw)

def get_bike_price(bike_type: str) -> int:
    if bike_type == "1":
        return 200
    elif bike_type == "2":
        return 300
    elif bike_type == "3":
        return 150
    else:
        return 0

def get_bike_name(bike_type: str) -> str:
    if bike_type == "1":
        return "городской"
    elif bike_type == "2":
        return "горный"
    elif bike_type == "3":
        return "детский"
    else:
        return "неизвестный"

def calculate_discount(hours: int) -> float:
    if hours >= 10:
        return 0.20
    elif hours >= 5:
        return 0.10
    else:
        return 0.0

def main() -> None:
    print("   Аренда велосипедов")

    client_name = input("Введите ваше имя: ").strip()
    bike_type = get_bike_type()
    hours = get_hours()

    price_per_hour = get_bike_price(bike_type)

    if price_per_hour == 0:
        print("Ошибка: выбран неизвестный тип велосипеда.")
        return

    if hours <= 0:
        print("Ошибка: количество часов должно быть положительным.")
        return

    bike_name = get_bike_name(bike_type)
    base_cost = price_per_hour * hours
    discount = calculate_discount(hours)
    discount_sum = base_cost * discount
    total = base_cost - discount_sum

    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(hours=hours)

    print()
    print(f"Клиент:            {client_name}")
    print(f"Тип велосипеда:    {bike_name}")
    print(f"Цена за час:       {price_per_hour} руб.")
    print(f"Количество часов:  {hours}")
    print(f"Начало аренды:     {start_time:%d.%m.%Y %H:%M}")
    print(f"Окончание аренды:  {end_time:%d.%m.%Y %H:%M}")
    print(f"Стоимость без скидки: {base_cost} руб.")
    if discount > 0:
        print(f"Скидка:            {int(discount * 100)}% ({discount_sum:.0f} руб.)")
    print(f"ИТОГО к оплате:    {total:.0f} руб.")
    print("Аренда успешно оформлена. Хорошей поездки!")

if __name__ == "__main__":
    main()