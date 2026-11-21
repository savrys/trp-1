"""Тесты главной страницы и кастомной страницы ошибки 404."""

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from web_bikes.models import Bike, Station
from web_rentals.models import Rental, User


class IndexViewTests(TestCase):
    """Проверка главной страницы."""

    def test_index_page_renders(self):
        response = self.client.get(reverse("web_main:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web_main/index.html")
        self.assertContains(response, "Bikely")


class Custom404Tests(TestCase):
    """Проверка кастомной страницы ошибки 404."""

    def test_unknown_url_returns_custom_page(self):
        response = self.client.get("/net-takoy-stranicy/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(
            response,
            "Страница не найдена",
            status_code=404,
        )
        self.assertContains(response, "На главную", status_code=404)

    def test_unknown_bike_returns_custom_page(self):
        response = self.client.get(
            reverse("web_bikes:detail", args=["unknown-bike"])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_unknown_rental_returns_custom_page(self):
        response = self.client.get(
            reverse("web_rentals:detail", args=[9999])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    @override_settings(DEBUG=True)
    def test_custom_page_is_shown_when_debug_enabled(self):
        response = self.client.get("/net-takoy-stranicy/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(
            response,
            "Страница не найдена",
            status_code=404,
        )
        self.assertNotContains(
            response,
            "You're seeing this error because you have",
            status_code=404,
        )


class ContextProcessorTests(TestCase):
    """Проверка общих данных сайта из контекстного процессора."""

    @classmethod
    def setUpTestData(cls):
        cls.center = Station.objects.create(name="Центр", capacity=20)
        Station.objects.create(name="Парк", capacity=10)
        Station.objects.create(name="Набережная", capacity=15)
        cls.urban = Bike.objects.create(
            model="City 100",
            type=Bike.Type.URBAN,
            is_available=True,
        )
        cls.mountain = Bike.objects.create(
            model="Trail 200",
            type=Bike.Type.MOUNTAIN,
            is_available=False,
        )
        cls.customer = User.objects.create(
            name="Анна",
            email="anna@example.com",
        )
        Rental.objects.create(
            bike=cls.mountain,
            user=cls.customer,
            station=cls.center,
            start_time=timezone.now(),
        )

    def test_context_contains_site_name_and_counts(self):
        response = self.client.get(reverse("web_main:index"))

        self.assertEqual(response.context["site_name"], "Bikely")
        self.assertEqual(response.context["bikes_count"], 2)
        self.assertEqual(
            response.context["bikely_stats"],
            {
                "bikes_total": 2,
                "bikes_available": 1,
                "rentals_total": 1,
                "rentals_active": 1,
                "rentals_completed": 0,
                "rentals_cancelled": 0,
            },
        )

    def test_context_is_available_on_other_pages(self):
        response = self.client.get(reverse("web_rentals:list"))

        self.assertEqual(response.context["site_name"], "Bikely")
        self.assertEqual(response.context["bikes_count"], 2)

    def test_navigation_and_footer_show_shared_data(self):
        response = self.client.get(reverse("web_main:index"))

        self.assertContains(response, "Велосипедов в парке: 2")
        self.assertContains(
            response,
            f"© {timezone.localdate().year} Bikely",
        )

    def test_index_avoids_n_plus_one_queries_for_stations(self):
        with self.assertNumQueries(3):
            response = self.client.get(reverse("web_main:index"))

        self.assertEqual(len(response.context["stations"]), 3)

    def test_index_shows_station_rental_statistics(self):
        response = self.client.get(reverse("web_main:index"))

        self.assertContains(response, "Оформлено аренд: 1")
        self.assertContains(response, "активных: 1")

