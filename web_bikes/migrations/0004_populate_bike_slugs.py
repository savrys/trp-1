"""Заполнение slug существующих велосипедов."""

from django.db import migrations
from django.utils.text import slugify
from unidecode import unidecode


def populate_bike_slugs(apps, schema_editor):
    """Сформировать уникальный slug из модели и первичного ключа."""
    Bike = apps.get_model("web_bikes", "Bike")

    for bike in Bike.objects.all().order_by("pk"):
        base_slug = slugify(unidecode(bike.model)) or "bike"
        bike.slug = f"{base_slug}-{bike.pk}"
        bike.save(update_fields=["slug"])


def clear_bike_slugs(apps, schema_editor):
    """Очистить slug при откате миграции."""
    Bike = apps.get_model("web_bikes", "Bike")

    Bike.objects.update(slug="")


class Migration(migrations.Migration):
    """Перенести существующие велосипеды на человекочитаемые адреса."""

    dependencies = [
        ("web_bikes", "0003_bike_slug"),
    ]

    operations = [
        migrations.RunPython(
            populate_bike_slugs,
            clear_bike_slugs,
        ),
    ]
