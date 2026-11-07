"""Модели предметной области: велосипеды и станции проката."""

from django.db import models


class Station(models.Model):
    """Станция проката велосипедов."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название станции",
    )

    capacity = models.PositiveIntegerField(
        verbose_name="Вместимость",
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Станция"
        verbose_name_plural = "Станции"


class Bike(models.Model):
    """Велосипед парка проката."""

    class Type(models.TextChoices):
        """Допустимые типы велосипедов."""

        MOUNTAIN = "Mountain", "Горный"
        TOURING = "Touring", "Туристический"
        URBAN = "Urban", "Городской"
        CHILD = "Child", "Детский"

    model = models.CharField(
        max_length=200,
        verbose_name="Модель",
    )

    type = models.CharField(
        max_length=50,
        choices=Type.choices,
        verbose_name="Тип",
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name="Доступен для аренды",
    )

    def __str__(self):
        return f"{self.model} ({self.get_type_display()})"

    class Meta:
        ordering = ["model"]
        verbose_name = "Велосипед"
        verbose_name_plural = "Велосипеды"

