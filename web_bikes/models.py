"""Модели предметной области: велосипеды и станции проката."""

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Case, Count, Q, Value, When
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode

# Вместимость, начиная с которой станция считается крупной.
LARGE_STATION_CAPACITY = 20


class StationQuerySet(models.QuerySet):
    """Набор запросов станций с готовыми аннотациями.

    Аннотации позволяют получать количество всех и активных аренд
    одним SQL-запросом и не обращаться к базе данных для каждой станции.
    """

    def with_rental_stats(self):
        """Дополнить станции количеством всех и активных аренд."""
        # Импорт внутри метода исключает циклический импорт приложений.
        from web_rentals.models import Rental

        return self.annotate(
            rentals_total=Count("rentals", distinct=True),
            rentals_active=Count(
                "rentals",
                filter=Q(rentals__status=Rental.Status.ACTIVE),
                distinct=True,
            ),
        )


class Station(models.Model):
    """Станция проката велосипедов."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название станции",
        help_text="Например: «Станция Парк Культуры».",
    )

    capacity = models.PositiveIntegerField(
        verbose_name="Вместимость",
        help_text=(
            f"Количество велосипедов, которое вмещает станция. "
            f"Станции от {LARGE_STATION_CAPACITY} мест считаются крупными."
        ),
        validators=[MinValueValidator(1)],
    )

    is_large = models.GeneratedField(
        expression=Case(
            When(
                capacity__gte=LARGE_STATION_CAPACITY,
                then=Value(True),
            ),
            default=Value(False),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Крупная станция",
    )

    objects = StationQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Станция"
        verbose_name_plural = "Станции"


class BikeQuerySet(models.QuerySet):
    """Набор запросов велосипедов с методами фильтрации и аннотаций."""

    def available(self):
        """Только велосипеды, отмеченные как свободные."""
        return self.filter(is_available=True)

    def available_on(self, day):
        """Свободные велосипеды на указанную дату.

        Велосипед блокирует только аренда со статусом «Активна».
        Завершённые и отменённые аренды доступность не ограничивают.
        """
        from web_rentals.models import Rental

        return self.available().exclude(
            rentals__status=Rental.Status.ACTIVE,
            rentals__start_time__date=day,
        )

    def with_rental_stats(self):
        """Дополнить велосипеды количеством всех и активных аренд."""
        from web_rentals.models import Rental

        return self.annotate(
            rentals_total=Count("rentals", distinct=True),
            rentals_active=Count(
                "rentals",
                filter=Q(rentals__status=Rental.Status.ACTIVE),
                distinct=True,
            ),
        )


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
        help_text="Например: «Format 1411».",
    )

    type = models.CharField(
        max_length=50,
        choices=Type.choices,
        verbose_name="Тип",
        help_text="Тип определяет назначение велосипеда.",
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name="Доступен для аренды",
        help_text="Снимите флажок, когда велосипед выдан клиенту.",
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        editable=False,
        verbose_name="URL-идентификатор",
    )

    objects = BikeQuerySet.as_manager()

    def __str__(self):
        return f"{self.model} ({self.get_type_display()})"

    def save(self, *args, **kwargs):
        """Сформировать slug при первом сохранении велосипеда."""
        # Повторно slug не пересоздаётся: адрес страницы остаётся стабильным.
        if not self.slug:
            # Транслитерируем название, затем приводим строку к формату URL.
            transliterated_model = unidecode(self.model)
            base_slug = slugify(transliterated_model) or "bike"

            if self.pk:
                self.slug = f"{base_slug}-{self.pk}"
            else:
                # Сначала сохраняем объект, чтобы база данных назначила pk.
                super().save(*args, **kwargs)
                self.slug = f"{base_slug}-{self.pk}"
                super().save(update_fields=["slug"])
                return

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Вернуть адрес подробной страницы велосипеда."""
        return reverse("web_bikes:detail", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["model"]
        verbose_name = "Велосипед"
        verbose_name_plural = "Велосипеды"

