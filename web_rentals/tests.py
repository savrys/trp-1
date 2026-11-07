"""Тесты моделей и представлений приложения web_rentals."""

from datetime import datetime

from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from web_bikes.models import Bike, Station

from .models import Rental, User


def aware(value):
    """Преобразовать строку в datetime с часовым поясом."""
    return timezone.make_aware(
        datetime.strptime(value, "%Y-%m-%d %H:%M")
    )


class RentalModelTests(TestCase):
    """Проверка моделей Rental и User."""

    @classmethod
    def setUpTestData(cls):
        cls.station = Station.objects.create(name="ВДНХ", capacity=20)
        cls.user = User.objects.create(
            name="Мария",
            email="maria@yandex.ru",
        )
        cls.bike = Bike.objects.create(
            model="Scott Aspect",
            type=Bike.Type.MOUNTAIN,
            is_available=False,
        )
        cls.rental = Rental.objects.create(
            bike=cls.bike,
            user=cls.user,
            station=cls.station,
            start_time=aware("2026-09-26 13:00"),
        )

    def test_str_contains_bike_user_and_station(self):
        text = str(self.rental)

        self.assertIn("Scott Aspect", text)
        self.assertIn("Мария", text)
        self.assertIn("ВДНХ", text)

    def test_is_active_property(self):
        self.assertTrue(self.rental.is_active)

        self.rental.is_completed = True
        self.assertFalse(self.rental.is_active)

    def test_complete_returns_bike_to_park(self):
        self.assertTrue(self.rental.complete())

        self.rental.refresh_from_db()
        self.bike.refresh_from_db()

        self.assertTrue(self.rental.is_completed)
        self.assertTrue(self.bike.is_available)

    def test_complete_is_idempotent(self):
        self.rental.complete()

        self.assertFalse(self.rental.complete())

    def test_delete_is_protected_by_rental(self):
        with self.assertRaises(ProtectedError):
            self.station.delete()

    def test_email_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create(
                    name="Дубль",
                    email="maria@yandex.ru",
                )

    def test_queryset_aggregation(self):
        stats = Rental.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(is_completed=False)),
        )

        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["active"], 1)

    def test_values_grouping_by_bike(self):
        rows = list(
            Rental.objects.values("bike__model").annotate(
                total=Count("id")
            )
        )

        self.assertEqual(
            rows,
            [{"bike__model": "Scott Aspect", "total": 1}],
        )


class RentalViewTests(TestCase):
    """Проверка списка, карточки и статистики аренд."""

    @classmethod
    def setUpTestData(cls):
        cls.station_center = Station.objects.create(
            name="Центр",
            capacity=10,
        )
        cls.station_park = Station.objects.create(
            name="Парк",
            capacity=20,
        )
        cls.anna = User.objects.create(
            name="Анна",
            email="anna@mail.ru",
        )
        cls.boris = User.objects.create(
            name="Борис",
            email="boris@mail.ru",
        )
        cls.city = Bike.objects.create(
            model="City 100",
            type=Bike.Type.URBAN,
        )
        cls.trail = Bike.objects.create(
            model="Trail 200",
            type=Bike.Type.MOUNTAIN,
        )
        cls.retro = Bike.objects.create(
            model="Retro 300",
            type=Bike.Type.URBAN,
        )

        cls.bikes = [cls.city, cls.trail, cls.retro]
        cls.users = [cls.anna, cls.boris]
        cls.stations = [cls.station_center, cls.station_park]

        cls.rentals = [
            Rental.objects.create(
                bike=cls.bikes[index % 3],
                user=cls.users[index % 2],
                station=cls.stations[index % 2],
                start_time=aware(
                    f"2026-09-{index + 1:02d} 10:00"
                ),
                is_completed=index % 2 == 1,
            )
            for index in range(7)
        ]

    def test_list_view_paginates_rentals(self):
        first_page = self.client.get(reverse("web_rentals:list"))
        second_page = self.client.get(
            reverse("web_rentals:list"),
            {"page": 2},
        )

        self.assertEqual(first_page.status_code, 200)
        self.assertTemplateUsed(
            first_page,
            "web_rentals/rental_list.html",
        )
        self.assertEqual(len(first_page.context["rentals"]), 5)
        self.assertEqual(len(second_page.context["rentals"]), 2)

    def test_list_view_calculates_statistics(self):
        response = self.client.get(reverse("web_rentals:list"))

        self.assertEqual(response.context["stats"]["total"], 7)
        self.assertEqual(response.context["stats"]["active"], 4)
        self.assertEqual(response.context["stats"]["completed"], 3)

    def test_list_view_default_ordering_is_newest_first(self):
        response = self.client.get(reverse("web_rentals:list"))

        self.assertEqual(
            response.context["rentals"][0],
            self.rentals[6],
        )

    def test_list_view_filters_by_status(self):
        active = self.client.get(
            reverse("web_rentals:list"),
            {"status": "active"},
        )
        completed = self.client.get(
            reverse("web_rentals:list"),
            {"status": "completed"},
        )

        self.assertTrue(
            all(
                not rental.is_completed
                for rental in active.context["rentals"]
            )
        )
        self.assertEqual(len(completed.context["rentals"]), 3)

    def test_list_view_filters_by_related_objects(self):
        by_bike = self.client.get(
            reverse("web_rentals:list"),
            {"bike": self.city.pk},
        )
        by_user = self.client.get(
            reverse("web_rentals:list"),
            {"user": self.anna.pk},
        )
        by_station = self.client.get(
            reverse("web_rentals:list"),
            {"station": self.station_park.pk},
        )

        self.assertEqual(
            by_bike.context["page_obj"].paginator.count,
            3,
        )
        self.assertEqual(
            by_user.context["page_obj"].paginator.count,
            4,
        )
        self.assertEqual(
            by_station.context["page_obj"].paginator.count,
            3,
        )

    def test_list_view_searches_related_fields(self):
        by_email = self.client.get(
            reverse("web_rentals:list"),
            {"search": "anna@mail.ru"},
        )
        by_bike = self.client.get(
            reverse("web_rentals:list"),
            {"search": "Trail"},
        )
        by_station = self.client.get(
            reverse("web_rentals:list"),
            {"search": "Парк"},
        )

        self.assertEqual(
            by_email.context["page_obj"].paginator.count,
            4,
        )
        self.assertEqual(
            by_bike.context["page_obj"].paginator.count,
            2,
        )
        self.assertEqual(
            by_station.context["page_obj"].paginator.count,
            3,
        )

    def test_list_view_sorts_by_related_object(self):
        by_date = self.client.get(
            reverse("web_rentals:list"),
            {"sort": "date_asc"},
        )
        by_bike = self.client.get(
            reverse("web_rentals:list"),
            {"sort": "bike"},
        )
        by_user = self.client.get(
            reverse("web_rentals:list"),
            {"sort": "user"},
        )

        self.assertEqual(
            by_date.context["rentals"][0],
            self.rentals[0],
        )
        self.assertEqual(
            by_bike.context["rentals"][0].bike.model,
            "City 100",
        )
        self.assertEqual(
            by_user.context["rentals"][0].user.name,
            "Анна",
        )

    def test_list_view_ignores_unknown_sorting(self):
        response = self.client.get(
            reverse("web_rentals:list"),
            {"sort": "unknown"},
        )

        self.assertEqual(response.context["sort"], "date")
        self.assertEqual(
            response.context["rentals"][0],
            self.rentals[6],
        )

    def test_pagination_keeps_selected_filters(self):
        response = self.client.get(
            reverse("web_rentals:list"),
            {"sort": "user"},
            HTTP_HOST="testserver",
        )

        self.assertContains(response, "sort=user")
        self.assertContains(response, "page=2")

    def test_detail_view_shows_related_objects(self):
        rental = self.rentals[0]
        response = self.client.get(
            reverse("web_rentals:detail", args=[rental.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "City 100")
        self.assertEqual(response.context["user_rentals_count"], 4)

    def test_detail_view_returns_404_for_unknown_rental(self):
        response = self.client.get(
            reverse("web_rentals:detail", args=[9999])
        )

        self.assertEqual(response.status_code, 404)

    def test_complete_view_closes_rental(self):
        rental = self.rentals[0]
        bike = rental.bike
        Bike.objects.filter(pk=bike.pk).update(is_available=False)

        response = self.client.post(
            reverse("web_rentals:complete", args=[rental.pk])
        )

        self.assertRedirects(
            response,
            reverse("web_rentals:detail", args=[rental.pk]),
        )

        rental.refresh_from_db()
        bike.refresh_from_db()

        self.assertTrue(rental.is_completed)
        self.assertTrue(bike.is_available)

    def test_complete_view_requires_post_method(self):
        response = self.client.get(
            reverse("web_rentals:complete", args=[self.rentals[0].pk])
        )

        self.assertEqual(response.status_code, 405)

    def test_statistics_view_aggregates_data(self):
        response = self.client.get(reverse("web_rentals:statistics"))

        self.assertEqual(response.status_code, 200)

        summary = response.context["summary"]
        self.assertEqual(summary["total"], 7)
        self.assertEqual(summary["active"], 4)
        self.assertEqual(summary["completed"], 3)
        self.assertEqual(summary["average_capacity"], 15)
        self.assertEqual(
            summary["last_start_time"],
            aware("2026-09-07 10:00"),
        )

        station_stats = {
            station.name: station
            for station in response.context["station_stats"]
        }
        self.assertEqual(station_stats["Центр"].rentals_total, 4)
        self.assertEqual(station_stats["Центр"].rentals_active, 4)
        self.assertEqual(station_stats["Парк"].rentals_total, 3)
        self.assertEqual(station_stats["Парк"].rentals_active, 0)

        user_stats = {
            user.name: user
            for user in response.context["user_stats"]
        }
        self.assertEqual(user_stats["Анна"].rentals_total, 4)
        self.assertEqual(user_stats["Борис"].rentals_total, 3)

        type_stats = {
            item["type_label"]: item
            for item in response.context["type_stats"]
        }
        self.assertEqual(type_stats["Городской"]["total"], 2)
        self.assertEqual(type_stats["Городской"]["available"], 2)
        self.assertEqual(type_stats["Горный"]["total"], 1)

