"""Перенос значений is_completed в новое поле status."""

from django.db import migrations


def migrate_rental_statuses(apps, schema_editor):
    """Завершённые аренды получают статус completed, остальные — active."""
    Rental = apps.get_model("web_rentals", "Rental")

    Rental.objects.filter(
        is_completed=True,
    ).update(
        status="completed",
    )
    Rental.objects.filter(
        is_completed=False,
    ).update(
        status="active",
    )


def reverse_rental_statuses(apps, schema_editor):
    """Восстановить булев признак завершения при откате миграции."""
    Rental = apps.get_model("web_rentals", "Rental")

    Rental.objects.filter(
        status="completed",
    ).update(
        is_completed=True,
    )
    Rental.objects.exclude(
        status="completed",
    ).update(
        is_completed=False,
    )


class Migration(migrations.Migration):
    """Перенести существующие статусы аренд без удаления записей."""

    dependencies = [
        ("web_rentals", "0002_rental_status"),
    ]

    operations = [
        migrations.RunPython(
            migrate_rental_statuses,
            reverse_rental_statuses,
        ),
    ]
