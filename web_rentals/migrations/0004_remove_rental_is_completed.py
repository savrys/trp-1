"""Удаление устаревшего булева поля is_completed."""

from django.db import migrations


class Migration(migrations.Migration):
    """Удалить is_completed после успешного переноса статусов."""

    dependencies = [
        ("web_rentals", "0003_migrate_rental_statuses"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="rental",
            name="is_completed",
        ),
    ]
