"""Контекстные процессоры, доступные во всех шаблонах сайта."""

from django.db.models import Count, Q

from web_bikes.models import Bike
from web_rentals.models import Rental


def bikely_context(request):
    """Передать в шаблоны общие сведения о сервисе Bikely.

    Показатели вычисляются средствами ORM при каждом запросе, поэтому
    остаются актуальными после изменения данных в административной панели.
    """
    bike_stats = Bike.objects.aggregate(
        bikes_total=Count("id"),
        bikes_available=Count("id", filter=Q(is_available=True)),
    )
    rental_stats = Rental.objects.statistics()

    return {
        "site_name": "Bikely",
        # Количество велосипедов востребовано в общей навигации.
        "bikes_count": bike_stats["bikes_total"],
        # Один словарь удобно использовать в шапке, на главной и в подвале.
        "bikely_stats": {
            "bikes_total": bike_stats["bikes_total"],
            "bikes_available": bike_stats["bikes_available"],
            "rentals_total": rental_stats["total"],
            "rentals_active": rental_stats["active"],
            "rentals_completed": rental_stats["completed"],
            "rentals_cancelled": rental_stats["cancelled"],
        },
    }
