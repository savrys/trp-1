"""Формы каталога велосипедов: фильтрация и загрузка изображений."""

from django import forms
from django.core.exceptions import ValidationError

from .models import Bike
from .validators import validate_bike_image

DEFAULT_SORT = "model"

BIKE_TYPE_CHOICES = (("", "Все типы"),) + tuple(Bike.Type.choices)

AVAILABILITY_CHOICES = (
    ("all", "Все велосипеды"),
    ("available", "Свободные"),
    ("rented", "На руках у клиентов"),
)

SORT_CHOICES = (
    ("model", "Модель (А–Я)"),
    ("-model", "Модель (Я–А)"),
    ("type", "Тип"),
    ("-type", "Тип (обратно)"),
    ("availability", "Доступность"),
)


class BikeFilterForm(forms.Form):
    """Форма поиска, фильтрации и сортировки каталога велосипедов."""

    search = forms.CharField(
        required=False,
        label="Поиск",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Модель или тип велосипеда",
            }
        ),
    )

    type = forms.ChoiceField(
        required=False,
        label="Тип",
        choices=BIKE_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    availability = forms.ChoiceField(
        required=False,
        label="Доступность",
        choices=AVAILABILITY_CHOICES,
        initial="all",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    sort = forms.ChoiceField(
        required=False,
        label="Сортировка",
        choices=SORT_CHOICES,
        initial=DEFAULT_SORT,
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class BikeForm(forms.ModelForm):
    """Создание и редактирование велосипеда с загрузкой изображения."""

    image = forms.FileField(
        required=False,
        label="Изображение",
        validators=[validate_bike_image],
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": "image/jpeg,image/png,image/webp",
            }
        ),
        help_text=(
            "Необязательное фото велосипеда в формате JPEG, PNG или WebP "
            "размером до 5 МБ."
        ),
    )

    class Meta:
        model = Bike
        fields = ("model", "type", "is_available", "image")
        widgets = {
            "model": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Например: Format 1411",
                }
            ),
            "type": forms.Select(attrs={"class": "form-select"}),
            "is_available": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
        labels = {
            "model": "Модель",
            "type": "Тип",
            "is_available": "Доступен для аренды",
        }
        help_texts = {
            "model": "Название модели велосипеда.",
            "is_available": (
                "Снимите флажок, если велосипед выдан клиенту."
            ),
        }

    def clean_model(self):
        """Убрать лишние пробелы и проверить осмысленность названия."""
        model = self.cleaned_data["model"].strip()

        if len(model) < 2:
            raise ValidationError(
                "Название модели должно содержать хотя бы два символа.",
                code="model_too_short",
            )

        return model
