"""Модели аренды: клиенты и факты аренды велосипедов."""

from django.db import models
from django.db.models import Count, Max, Q
from django.utils import timezone

from web_bikes.models import Bike, Station


class UserQuerySet(models.QuerySet):
    """Набор запросов клиентов с агрегированной статистикой аренд."""

    def with_rental_stats(self):
        """Дополнить клиентов количеством всех и активных аренд."""
        return self.annotate(
            rentals_total=Count("rentals", distinct=True),
            rentals_active=Count(
                "rentals",
                filter=Q(rentals__status=Rental.Status.ACTIVE),
                distinct=True,
            ),
        )


class User(models.Model):
    """Клиент сервиса проката велосипедов."""

    name = models.CharField(
        max_length=200,
        verbose_name="Имя клиента",
        help_text="Фамилия и имя клиента для обращений и отчётов.",
    )

    email = models.EmailField(
        unique=True,
        verbose_name="Электронная почта",
        help_text="Адрес уникален: по нему клиент находится в базе.",
    )

    objects = UserQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class RentalQuerySet(models.QuerySet):
    """Пользовательский QuerySet аренд.

    Методы скрывают повторяющиеся условия фильтрации и позволяют
    строить запросы в представлениях и административной панели.
    """

    def active(self):
        """Только активные аренды."""
        return self.filter(status=Rental.Status.ACTIVE)

    def completed(self):
        """Только завершённые аренды."""
        return self.filter(status=Rental.Status.COMPLETED)

    def cancelled(self):
        """Только отменённые аренды."""
        return self.filter(status=Rental.Status.CANCELLED)

    def with_related(self):
        """Загрузить аренду вместе с велосипедом, клиентом и станцией."""
        return self.select_related("bike", "user", "station")

    def for_bike(self, bike):
        """Аренды указанного велосипеда."""
        return self.filter(bike=bike)

    def for_user(self, user):
        """Аренды указанного клиента."""
        return self.filter(user=user)

    def for_station(self, station):
        """Аренды, оформленные на указанной станции."""
        return self.filter(station=station)

    def in_period(self, start=None, end=None):
        """Аренды за период по дате начала (границы необязательны)."""
        if start is not None:
            self = self.filter(start_time__date__gte=start)
        if end is not None:
            self = self.filter(start_time__date__lte=end)
        return self

    def statistics(self):
        """Сводные показатели аренд по статусам одним запросом."""
        return self.aggregate(
            total=Count("id"),
            active=Count(
                "id",
                filter=Q(status=Rental.Status.ACTIVE),
            ),
            completed=Count(
                "id",
                filter=Q(status=Rental.Status.COMPLETED),
            ),
            cancelled=Count(
                "id",
                filter=Q(status=Rental.Status.CANCELLED),
            ),
            last_start_time=Max("start_time"),
        )


class Rental(models.Model):
    """Аренда велосипеда конкретным клиентом на станции."""

    class Status(models.TextChoices):
        """Статусы аренды."""

        ACTIVE = "active", "Активна"
        COMPLETED = "completed", "Завершена"
        CANCELLED = "cancelled", "Отменена"

    bike = models.ForeignKey(
        Bike,
        on_delete=models.PROTECT,
        related_name="rentals",
        verbose_name="Велосипед",
        help_text="Выданный клиенту велосипед.",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="rentals",
        verbose_name="Клиент",
        help_text="Клиент, оформивший аренду.",
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.PROTECT,
        related_name="rentals",
        verbose_name="Станция",
        help_text="Станция выдачи велосипеда.",
    )

    start_time = models.DateTimeField(
        default=timezone.now,
        verbose_name="Время начала",
        help_text="Дата и время выдачи велосипеда клиенту.",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name="Статус аренды",
        help_text=(
            "Активная аренда блокирует велосипед, "
            "завершённая и отменённая — нет."
        ),
    )

    objects = RentalQuerySet.as_manager()

    @property
    def is_active(self):
        """Признак активной аренды."""
        return self.status == self.Status.ACTIVE

    def complete(self):
        """Завершить активную аренду и вернуть велосипед в парк.

        Возвращает True, если аренда была завершена этим вызовом.
        """
        if self.status != self.Status.ACTIVE:
            return False

        self.status = self.Status.COMPLETED
        self.save(update_fields=["status"])

        # Возвращаем велосипед в парк средствами ORM.
        Bike.objects.filter(pk=self.bike_id).update(is_available=True)
        return True

    def cancel(self):
        """Отменить активную аренду и вернуть велосипед в парк.

        Возвращает True, если аренда была отменена этим вызовом.
        """
        if self.status != self.Status.ACTIVE:
            return False

        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])

        Bike.objects.filter(pk=self.bike_id).update(is_available=True)
        return True

    def __str__(self):
        return (
            f"Аренда №{self.pk} — {self.bike.model} "
            f"({self.user.name}, {self.station.name})"
        )

    class Meta:
        ordering = ["-start_time", "pk"]
        verbose_name = "Аренда"
        verbose_name_plural = "Аренды"
        indexes = [
            models.Index(
                fields=["status", "-start_time"],
                name="rental_status_start_idx",
            ),
        ]
