from django.http import HttpResponse
from web_main.views import page
from storage import load_rentals


def get_rental_by_id(rentals_list, rental_id):
    """Вспомогательная функция поиска транзакции аренды по её ID"""
    for rental in rentals_list:
        if rental.id == rental_id:
            return rental
    return None


def rentals_list_view(request):
    """Страница отображения всех сессий аренды"""
    rentals = load_rentals("data/rentals.json")

    items = ""
    for r in rentals:
        is_closed = getattr(r, 'is_closed', False)
        status_text = "Завершена" if is_closed else "Активна"
        badge_class = "bg-secondary" if is_closed else "bg-success"

        # Получаем имя модели из связанного объекта (разработка ПР3)
        bike_model = getattr(r.bike, 'model', f"ID {r.bike_id}")

        items += f"""
        <li class="list-group-item d-flex justify-content-between
            align-items-center">
            <a href="/rentals/{r.id}/" class="fw-bold">
                Сессия проката №{r.id} (Велосипед: {bike_model})
            </a>
            <span class="badge {badge_class}">{status_text}</span>
        </li>
        """
    content = f"""
    <h1>Велосипеды и Станции проката</h1>
    <ul class="list-group shadow-sm mt-3">{items}</ul>
    """
    return HttpResponse(page("Журнал аренды – BikeRent", content))


def rental_detail_view(request, rental_id):
    """Страница деталей по конкретной выбранной аренде"""
    rentals = load_rentals("data/rentals.json")
    rental = get_rental_by_id(rentals, rental_id)

    if rental is None:
        content = """
        <h1 class="text-danger">Запись об аренде не найдена</h1>
        <p class="lead">Сессии аренды с указанным ID не зарегистрировано.</p>
        <a href="/rentals/" class="btn btn-outline-secondary mt-3">
            ← К списку записей
        </a>
        """
        return HttpResponse(page("Аренда не найдена", content), status=404)

    is_closed = getattr(rental, 'is_closed', False)
    bike_id_str = f'Велосипед ID {rental.bike_id}'
    bike_model = getattr(rental.bike, 'model', bike_id_str)
    user_id_str = f'Пользователь ID {rental.user_id}'
    user_name = getattr(rental.user, 'name', user_id_str)

    status_desc = (
        'Закрыта (Транспорт возвращен на станцию)' if is_closed
        else 'В процессе (Пользователь еще катается)'
    )

    badge_bg = 'bg-secondary' if is_closed else 'bg-success'

    content = f"""
    <div class="card shadow-sm border-info mt-3">
        <div class="card-header bg-info text-white">
            <h5>Информация об арендной сессии №{rental.id}</h5>
        </div>
        <div class="card-body">
            <p><strong>Арендованный велосипед:</strong> {bike_model}</p>
            <p><strong>Пользователь (Арендатор):</strong> {user_name}</p>
            <p><strong>Дата транзакции:</strong>
                {getattr(rental, 'date', 'Не указана')}
            </p>
            <p><strong>Текущее состояние сессии:</strong>
                <span class="badge {badge_bg} p-2">
                    {status_desc}
                </span>
            </p>
            <a href="/rentals/" class="btn btn-outline-secondary mt-3">
                ← Назад к журналу
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(f"Аренда №{rental.id}", content), status=200)
