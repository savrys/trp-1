"""Тесты моделей и представлений приложения web_bikes."""

from datetime import datetime

from django.db.models import Count
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from web_rentals.models import Rental, User

from .models import Bike, Station


def aware(value):
    """Преобразовать строку в datetime с часовым поясом."""
    return timezone.make_aware(
        datetime.strptime(value, "%Y-%m-%d %H:%M")
    )


class BikeModelTests(TestCase):
    """Проверка моделей Bike и Station."""

    @classmethod
    def setUpTestData(cls):
        cls.station = Station.objects.create(
            name="Парк Горького",
            capacity=15,
        )
        cls.user = User.objects.create(
            name="Иван",
            email="ivan@mail.ru",
        )
        cls.urban = Bike.objects.create(
            model="Aist City",
            type=Bike.Type.URBAN,
            is_available=True,
        )
        cls.mountain = Bike.objects.create(
            model="Stels Navigator",
            type=Bike.Type.MOUNTAIN,
            is_available=False,
        )
        cls.rental = Rental.objects.create(
            bike=cls.mountain,
            user=cls.user,
            station=cls.station,
            start_time=aware("2026-09-26 12:00"),
        )

    def test_str_returns_human_readable_name(self):
        self.assertEqual(str(self.urban), "Aist City (Городской)")
        self.assertEqual(str(self.station), "Парк Горького")

    def test_type_choices_have_russian_labels(self):
        self.assertEqual(Bike.Type.MOUNTAIN.label, "Горный")
        self.assertEqual(
            self.mountain.get_type_display(),
            "Горный",
        )

    def test_availability_defaults_to_true(self):
        bike = Bike.objects.create(
            model="Forward Apache",
            type=Bike.Type.TOURING,
        )
        self.assertTrue(bike.is_available)

    def test_default_ordering_by_model(self):
        self.assertEqual(
            list(Bike.objects.all()),
            [self.urban, self.mountain],
        )

    def test_filter_and_exclude(self):
        self.assertEqual(
            list(Bike.objects.filter(is_available=True)),
            [self.urban],
        )
        self.assertEqual(
            list(Bike.objects.exclude(is_available=True)),
            [self.mountain],
        )

    def test_lookup_by_related_field(self):
        rented_bikes = Bike.objects.filter(
            rentals__is_completed=False
        ).distinct()
        self.assertEqual(list(rented_bikes), [self.mountain])

    def test_annotate_counts_related_rentals(self):
        station = Station.objects.annotate(
            rentals_count=Count("rentals"),
        ).get(pk=self.station.pk)
        self.assertEqual(station.rentals_count, 1)


class BikeViewTests(TestCase):
    """Проверка страниц каталога велосипедов."""

    @classmethod
    def setUpTestData(cls):
        cls.station = Station.objects.create(name="Центр", capacity=10)
        cls.user = User.objects.create(
            name="Анна",
            email="anna@mail.ru",
        )
        cls.city = Bike.objects.create(
            model="City 100",
            type=Bike.Type.URBAN,
            is_available=True,
        )
        cls.trail = Bike.objects.create(
            model="Trail 200",
            type=Bike.Type.MOUNTAIN,
            is_available=True,
        )
        cls.retro = Bike.objects.create(
            model="Retro 300",
            type=Bike.Type.URBAN,
            is_available=False,
        )
        Rental.objects.create(
            bike=cls.retro,
            user=cls.user,
            station=cls.station,
            start_time=aware("2026-09-26 14:00"),
        )

    def test_list_view_returns_all_bikes(self):
        response = self.client.get(reverse("web_bikes:list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web_bikes/bike_list.html")
        self.assertEqual(len(response.context["bikes"]), 3)

    def test_list_view_supports_search(self):
        response = self.client.get(
            reverse("web_bikes:list"),
            {"search": "trail"},
        )

        self.assertEqual(
            [bike.model for bike in response.context["bikes"]],
            ["Trail 200"],
        )

    def test_list_view_filters_by_type(self):
        response = self.client.get(
            reverse("web_bikes:list"),
            {"type": Bike.Type.URBAN},
        )

        self.assertEqual(
            {bike.model for bike in response.context["bikes"]},
            {"City 100", "Retro 300"},
        )
        self.assertEqual(
            response.context["selected_type_label"],
            "Городской",
        )
        self.assertContains(response, "Городской")

    def test_list_view_filters_by_availability(self):
        response = self.client.get(
            reverse("web_bikes:list"),
            {"availability": "rented"},
        )

        self.assertEqual(
            [bike.model for bike in response.context["bikes"]],
            ["Retro 300"],
        )

    def test_list_view_sorts_descending_by_model(self):
        response = self.client.get(
            reverse("web_bikes:list"),
            {"sort": "-model"},
        )

        self.assertEqual(
            [bike.model for bike in response.context["bikes"]],
            ["Trail 200", "Retro 300", "City 100"],
        )

    def test_list_view_ignores_unknown_sorting(self):
        response = self.client.get(
            reverse("web_bikes:list"),
            {"sort": "unknown"},
        )

        self.assertEqual(response.context["sort"], "model")
        self.assertEqual(
            [bike.model for bike in response.context["bikes"]],
            ["City 100", "Retro 300", "Trail 200"],
        )

    def test_detail_view_shows_bike_and_rental_history(self):
        response = self.client.get(
            reverse("web_bikes:detail", args=[self.retro.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Retro 300")
        self.assertEqual(len(response.context["rental_history"]), 1)

    def test_detail_view_returns_404_for_unknown_bike(self):
        response = self.client.get(
            reverse("web_bikes:detail", args=[9999])
        )

        self.assertEqual(response.status_code, 404)

