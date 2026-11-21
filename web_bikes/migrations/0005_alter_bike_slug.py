"""Обеспечение уникальности slug велосипедов."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Добавить ограничение unique после заполнения всех значений."""

    dependencies = [
        ("web_bikes", "0004_populate_bike_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bike",
            name="slug",
            field=models.SlugField(
                editable=False,
                max_length=255,
                unique=True,
                verbose_name="URL-идентификатор",
            ),
        ),
    ]
