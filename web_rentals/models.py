"""Модели аренды: клиенты и факты аренды велосипедов."""

from django.db import models

from web_bikes.models import Bike, Station


class User(models.Model):
    """Клиент сервиса проката велосипедов."""

    name = models.CharField(
        max_length=200,
        verbose_name="Имя клиента",
    )

    email = models.EmailField(
        unique=True,
        verbose_name="Электронная почта",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Rental(models.Model):
    """Аренда велосипеда конкретным клиентом на станции."""

    bike = models.ForeignKey(
        Bike,
        on_delete=models.PROTECT,
        related_name="rentals",
        verbose_name="Велосипед",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="rentals",
        verbose_name="Клиент",
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.PROTECT,
        related_name="rentals",
        verbose_name="Станция",
    )

    start_time = models.DateTimeField(
        verbose_name="Время начала",
    )

    is_completed = models.BooleanField(
        default=False,
        verbose_name="Аренда завершена",
    )

    @property
    def is_active(self):
        """Признак незавершённой аренды."""
        return not self.is_completed

    def complete(self):
        """Завершить аренду и вернуть велосипед в парк.

        Возвращает True, если аренда была завершена этим вызовом.
        """
        if self.is_completed:
            return False

        self.is_completed = True
        self.save(update_fields=["is_completed"])

        # Возвращаем велосипед в парк средствами ORM.
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

