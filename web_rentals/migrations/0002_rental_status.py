"""Добавление статуса аренды вместо булева признака завершения."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Добавить поле status, сохранив is_completed для переноса данных."""

    dependencies = [
        ("web_rentals", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="rental",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Активна"),
                    ("completed", "Завершена"),
                    ("cancelled", "Отменена"),
                ],
                db_index=True,
                default="active",
                help_text=(
                    "Активная аренда блокирует велосипед, "
                    "завершённая и отменённая — нет."
                ),
                max_length=20,
                verbose_name="Статус аренды",
            ),
        ),
        migrations.AddIndex(
            model_name="rental",
            index=models.Index(
                fields=["status", "-start_time"],
                name="rental_status_start_idx",
            ),
        ),
    ]
