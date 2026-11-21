"""Добавление временного поля slug для велосипедов."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Добавить slug без ограничения уникальности для заполнения данных."""

    dependencies = [
        ("web_bikes", "0002_station_is_large"),
    ]

    operations = [
        migrations.AddField(
            model_name="bike",
            name="slug",
            field=models.SlugField(
                blank=True,
                default="",
                editable=False,
                max_length=255,
                verbose_name="URL-идентификатор",
            ),
        ),
    ]
