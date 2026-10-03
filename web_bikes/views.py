from django.http import HttpResponse
from web_main.views import page
from storage import load_bikes, load_stations


def get_bike_by_id(bikes_list, bike_id):
    """Вспомогательная функция поиска велосипеда по его ID"""
    for bike in bikes_list:
        if bike.id == bike_id:
            return bike
    return None


def bikes_list_view(request):
    """Страница со списком всех велосипедов и станций сети проката"""
    bikes = load_bikes("data/bikes.json")
    stations = load_stations("data/stations.json")

    bike_items = ""
    for b in bikes:
        # Проверяем статус велосипеда (активен/свободен/занят)
        is_avail = getattr(b, "is_available", True)
        status_text = "Доступен" if is_avail else "В прокате"
        status_color = "text-success" if is_avail else "text-danger"

        bike_items += f"""
        <li class="list-group-item">
            <a href="/bikes/{b.id}/" class="fw-bold">{b.model}</a>
            (ID: {b.id}) <br>
            Статус: <span class="{status_color}">{status_text}</span>
        </li>
        """

    station_items = ""
    for s in stations:
        station_items += (
            f'<li class="list-group-item">📌 <strong>{s.name}</strong> '
            f'(Вместимость: {s.capacity} мест)</li>'
        )

    content = f"""
    <h1>Велосипеды и Станции проката</h1>
    <div class="row mt-4">
        <div class="col-md-6 mb-4">
            <h3>Велосипеды в системе</h3>
            <ul class="list-group shadow-sm">{bike_items}</ul>
        </div>
        <div class="col-md-6 mb-4">
            <h3>Станции проката сети</h3>
            <ul class="list-group shadow-sm">{station_items}</ul>
        </div>
    </div>
    """
    return HttpResponse(page("Велосипеды – BikeRent", content))


def bike_detail_view(request, bike_id):
    """Детальная страница информации об отдельном велосипеде"""
    bikes = load_bikes("data/bikes.json")
    bike = get_bike_by_id(bikes, bike_id)

    if bike is None:
        content = """
        <h1 class="text-danger">Велосипед не найден</h1>
        <p class="lead">Велосипеда с указанным ID не существует.</p>
        <a href="/bikes/" class="btn btn-outline-secondary mt-3">
            ← Вернуться к каталогу
        </a>
        """
        return HttpResponse(page("Велосипед не найден", content), status=404)

    is_avail = getattr(bike, 'is_available', True)
    badge_bg = 'bg-success' if is_avail else 'bg-danger'
    status_desc = (
        'Свободен для выдачи' if is_avail
        else 'Находится на руках у клиента'
    )

    content = f"""
    <div class="card shadow-sm border-primary mt-3">
        <div class="card-body">
            <h5 class="card-title display-6">{bike.model}</h5>
            <hr>
            <p class="card-text"><strong>ID объекта:</strong> {bike.id}</p>
            <p class="card-text">
                <strong>Текущий статус проката:</strong>
                <span class="badge {badge_bg} p-2">
                    {status_desc}
                </span>
            </p>
            <a href="/bikes/" class="btn btn-outline-primary mt-3">
                ← К списку велосипедов
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(f"Велосипед {bike.model}", content), status=200)
