"""Добавление вычисляемого признака крупной станции."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Создать GeneratedField is_large на основе вместимости станции."""

    dependencies = [
        ("web_bikes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="station",
            name="is_large",
            field=models.GeneratedField(
                db_persist=True,
                expression=models.Case(
                    models.When(capacity__gte=20, then=models.Value(True)),
                    default=models.Value(False),
                    output_field=models.BooleanField(),
                ),
                output_field=models.BooleanField(),
                verbose_name="Крупная станция",
            ),
        ),
    ]
