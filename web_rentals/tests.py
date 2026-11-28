"""Тесты моделей и представлений приложения web_rentals."""

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from web_bikes.models import Bike, Station

from .forms import RentalForm
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

    def test_status_defaults_to_active(self):
        self.assertEqual(self.rental.status, Rental.Status.ACTIVE)
        self.assertTrue(self.rental.is_active)

    def test_is_active_property_depends_on_status(self):
        self.rental.status = Rental.Status.COMPLETED
        self.assertFalse(self.rental.is_active)

        self.rental.status = Rental.Status.CANCELLED
        self.assertFalse(self.rental.is_active)

    def test_complete_returns_bike_to_park(self):
        self.assertTrue(self.rental.complete())

        self.rental.refresh_from_db()
        self.bike.refresh_from_db()

        self.assertEqual(self.rental.status, Rental.Status.COMPLETED)
        self.assertFalse(self.rental.is_active)
        self.assertTrue(self.bike.is_available)

    def test_cancel_returns_bike_to_park(self):
        self.bike.is_available = False
        self.bike.save(update_fields=["is_available"])

        self.assertTrue(self.rental.cancel())

        self.rental.refresh_from_db()
        self.bike.refresh_from_db()

        self.assertEqual(self.rental.status, Rental.Status.CANCELLED)
        self.assertTrue(self.bike.is_available)

    def test_complete_and_cancel_keep_database_record(self):
        rental_pk = self.rental.pk

        self.rental.complete()

        self.assertTrue(Rental.objects.filter(pk=rental_pk).exists())

    def test_complete_is_idempotent(self):
        self.rental.complete()

        self.assertFalse(self.rental.complete())
        self.assertFalse(self.rental.cancel())

    def test_status_queryset_methods_filter_records(self):
        completed = Rental.objects.create(
            bike=self.bike,
            user=self.user,
            station=self.station,
            start_time=aware("2026-09-27 13:00"),
            status=Rental.Status.COMPLETED,
        )
        cancelled = Rental.objects.create(
            bike=self.bike,
            user=self.user,
            station=self.station,
            start_time=aware("2026-09-28 13:00"),
            status=Rental.Status.CANCELLED,
        )

        self.assertEqual(list(Rental.objects.active()), [self.rental])
        self.assertEqual(list(Rental.objects.completed()), [completed])
        self.assertEqual(list(Rental.objects.cancelled()), [cancelled])

    def test_statistics_counts_each_status(self):
        Rental.objects.create(
            bike=self.bike,
            user=self.user,
            station=self.station,
            start_time=aware("2026-09-27 13:00"),
            status=Rental.Status.COMPLETED,
        )
        Rental.objects.create(
            bike=self.bike,
            user=self.user,
            station=self.station,
            start_time=aware("2026-09-28 13:00"),
            status=Rental.Status.CANCELLED,
        )

        stats = Rental.objects.statistics()

        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["active"], 1)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["cancelled"], 1)
        self.assertEqual(stats["last_start_time"], aware("2026-09-28 13:00"))

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
            active=Count(
                "id",
                filter=Q(status=Rental.Status.ACTIVE),
            ),
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
                status=cls.rental_status(index),
            )
            for index in range(7)
        ]

    @staticmethod
    def rental_status(index):
        """Распределить тестовые аренды по всем трём статусам."""
        if index == 2:
            return Rental.Status.CANCELLED
        if index % 2 == 1:
            return Rental.Status.COMPLETED
        return Rental.Status.ACTIVE

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
        self.assertEqual(response.context["stats"]["active"], 3)
        self.assertEqual(response.context["stats"]["completed"], 3)
        self.assertEqual(response.context["stats"]["cancelled"], 1)

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
        cancelled = self.client.get(
            reverse("web_rentals:list"),
            {"status": "cancelled"},
        )

        self.assertTrue(
            all(
                rental.status == Rental.Status.ACTIVE
                for rental in active.context["rentals"]
            )
        )
        self.assertEqual(len(completed.context["rentals"]), 3)
        self.assertEqual(len(cancelled.context["rentals"]), 1)

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

        self.assertEqual(rental.status, Rental.Status.COMPLETED)
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
        self.assertEqual(summary["active"], 3)
        self.assertEqual(summary["completed"], 3)
        self.assertEqual(summary["cancelled"], 1)
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
        self.assertEqual(station_stats["Центр"].rentals_active, 3)
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


class RentalFormTests(TestCase):
    """Проверка валидации формы аренды."""

    def setUp(self):
        self.station = Station.objects.create(name="Форма", capacity=10)
        self.user = User.objects.create(
            name="Клиент формы",
            email="form@example.com",
        )
        self.bike = Bike.objects.create(
            model="Form Bike",
            type=Bike.Type.URBAN,
        )

    def future_start(self):
        return (
            timezone.localtime() + timedelta(days=2)
        ).strftime("%Y-%m-%dT%H:%M")

    def form_data(self, **overrides):
        data = {
            "bike": self.bike.pk,
            "user": self.user.pk,
            "station": self.station.pk,
            "start_time": self.future_start(),
        }
        data.update(overrides)
        return data

    def test_valid_form_creates_active_rental(self):
        form = RentalForm(data=self.form_data())

        self.assertTrue(form.is_valid(), form.errors)

        rental = form.save()

        self.assertEqual(rental.status, Rental.Status.ACTIVE)

    def test_start_time_in_past_is_rejected(self):
        past = (
            timezone.localtime() - timedelta(days=1)
        ).strftime("%Y-%m-%dT%H:%M")
        form = RentalForm(data=self.form_data(start_time=past))

        self.assertFalse(form.is_valid())
        self.assertIn("start_time", form.errors)

    def test_station_capacity_is_validated(self):
        station = Station.objects.create(name="Маленькая", capacity=1)
        Rental.objects.create(
            bike=self.bike,
            user=self.user,
            station=station,
            start_time=timezone.localtime() + timedelta(days=1),
        )
        another_bike = Bike.objects.create(
            model="Another Bike",
            type=Bike.Type.MOUNTAIN,
        )

        form = RentalForm(
            data=self.form_data(
                bike=another_bike.pk,
                station=station.pk,
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("station", form.errors)


class RentalFormViewTests(TestCase):
    """Проверка представлений создания, редактирования и отмены аренды."""

    def setUp(self):
        self.station = Station.objects.create(
            name="Станция формы",
            capacity=10,
        )
        self.user = User.objects.create(
            name="Тестовый клиент",
            email="rental-form@example.com",
        )
        self.bike = Bike.objects.create(
            model="Form City",
            type=Bike.Type.URBAN,
        )
        self.another_bike = Bike.objects.create(
            model="Form Trail",
            type=Bike.Type.MOUNTAIN,
        )
        self.start_time = timezone.localtime() + timedelta(days=2)

    def form_data(self, **overrides):
        data = {
            "bike": self.bike.pk,
            "user": self.user.pk,
            "station": self.station.pk,
            "start_time": self.start_time.strftime("%Y-%m-%dT%H:%M"),
        }
        data.update(overrides)
        return data

    def test_create_view_marks_bike_unavailable(self):
        response = self.client.post(
            reverse("web_rentals:create"),
            self.form_data(),
        )

        rental = Rental.objects.get(bike=self.bike)

        self.assertRedirects(
            response,
            reverse("web_rentals:detail", args=[rental.pk]),
        )
        self.assertEqual(rental.status, Rental.Status.ACTIVE)

        self.bike.refresh_from_db()
        self.assertFalse(self.bike.is_available)

    def test_create_view_rejects_busy_bike(self):
        Rental.objects.create(
            bike=self.bike,
            user=self.user,
            station=self.station,
            start_time=self.start_time,
        )
        self.bike.is_available = False
        self.bike.save(update_fields=["is_available"])

        response = self.client.post(
            reverse("web_rentals:create"),
            self.form_data(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже находится в активной аренде")
        self.assertEqual(Rental.objects.count(), 1)

    def test_update_view_excludes_current_rental_from_conflict_check(self):
        rental = Rental.objects.create(
            bike=self.bike,
            user=self.user,
            station=self.station,
            start_time=self.start_time,
        )
        self.bike.is_available = False
        self.bike.save(update_fields=["is_available"])

        response = self.client.post(
            reverse("web_rentals:edit", args=[rental.pk]),
            self.form_data(),
        )

        self.assertRedirects(
            response,
            reverse("web_rentals:detail", args=[rental.pk]),
        )
        self.assertEqual(Rental.objects.count(), 1)

        rental.refresh_from_db()
        self.assertEqual(rental.bike_id, self.bike.pk)

    def test_update_view_switches_bike_and_availability(self):
        rental = Rental.objects.create(
            bike=self.bike,
            user=self.user,
            station=self.station,
            start_time=self.start_time,
        )
        self.bike.is_available = False
        self.bike.save(update_fields=["is_available"])

        response = self.client.post(
            reverse("web_rentals:edit", args=[rental.pk]),
            self.form_data(bike=self.another_bike.pk),
        )

        self.assertRedirects(
            response,
            reverse("web_rentals:detail", args=[rental.pk]),
        )

        rental.refresh_from_db()
        self.bike.refresh_from_db()
        self.another_bike.refresh_from_db()

        self.assertEqual(rental.bike_id, self.another_bike.pk)
        self.assertTrue(self.bike.is_available)
        self.assertFalse(self.another_bike.is_available)

    def test_update_view_rejects_bike_from_another_active_rental(self):
        rental = Rental.objects.create(
            bike=self.bike,
            user=self.user,
            station=self.station,
            start_time=self.start_time,
        )
        self.another_bike.is_available = False
        self.another_bike.save(update_fields=["is_available"])
        Rental.objects.create(
            bike=self.another_bike,
            user=self.user,
            station=self.station,
            start_time=self.start_time,
        )

        response = self.client.post(
            reverse("web_rentals:edit", args=[rental.pk]),
            self.form_data(bike=self.another_bike.pk),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже находится в активной аренде")

        rental.refresh_from_db()
        self.assertEqual(rental.bike_id, self.bike.pk)

    def test_cancel_view_returns_bike_to_park(self):
        rental = Rental.objects.create(
            bike=self.bike,
            user=self.user,
            station=self.station,
            start_time=self.start_time,
        )
        self.bike.is_available = False
        self.bike.save(update_fields=["is_available"])

        response = self.client.post(
            reverse("web_rentals:cancel", args=[rental.pk]),
        )

        self.assertRedirects(
            response,
            reverse("web_rentals:detail", args=[rental.pk]),
        )

        rental.refresh_from_db()
        self.bike.refresh_from_db()

        self.assertEqual(rental.status, Rental.Status.CANCELLED)
        self.assertTrue(self.bike.is_available)

    def test_cancel_view_requires_post(self):
        rental = Rental.objects.create(
            bike=self.bike,
            user=self.user,
            station=self.station,
            start_time=self.start_time,
        )

        response = self.client.get(
            reverse("web_rentals:cancel", args=[rental.pk]),
        )

        self.assertEqual(response.status_code, 405)



class RentalAdminTests(TestCase):
    """Проверка административных действий и статистики аренд."""

    @classmethod
    def setUpTestData(cls):
        cls.station = Station.objects.create(name="Админ-станция", capacity=10)
        cls.bike = Bike.objects.create(
            model="Admin Bike",
            type=Bike.Type.URBAN,
            is_available=False,
        )
        cls.rental = Rental.objects.create(
            bike=cls.bike,
            user=User.objects.create(
                name="Админ Клиент",
                email="client@example.com",
            ),
            station=cls.station,
            start_time=aware("2026-09-10 09:00"),
        )
        cls.admin_user = get_user_model().objects.create_superuser(
            username="rental-admin",
            email="rental-admin@example.com",
            password="admin-password",
        )

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_rental_changelist_shows_status_and_bike_type(self):
        response = self.client.get(
            reverse("admin:web_rentals_rental_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Активна")
        self.assertContains(response, "Городской")

    def test_user_changelist_shows_rental_statistics(self):
        response = self.client.get(
            reverse("admin:web_rentals_user_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Всего аренд")
        self.assertContains(response, "Активных аренд")
        self.assertContains(response, "Админ Клиент")

    def test_complete_action_updates_status_and_bike(self):
        response = self.client.post(
            reverse("admin:web_rentals_rental_changelist"),
            {
                "action": "complete_rentals",
                "_selected_action": [str(self.rental.pk)],
                "select_across": "0",
                "index": "0",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.rental.refresh_from_db()
        self.bike.refresh_from_db()

        self.assertEqual(self.rental.status, Rental.Status.COMPLETED)
        self.assertTrue(self.bike.is_available)

    def test_cancel_action_updates_status_and_bike(self):
        response = self.client.post(
            reverse("admin:web_rentals_rental_changelist"),
            {
                "action": "cancel_rentals",
                "_selected_action": [str(self.rental.pk)],
                "select_across": "0",
                "index": "0",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.rental.refresh_from_db()
        self.bike.refresh_from_db()

        self.assertEqual(self.rental.status, Rental.Status.CANCELLED)
        self.assertTrue(self.bike.is_available)

