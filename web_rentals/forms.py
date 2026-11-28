"""Формы аренды: фильтрация списка и создание/редактирование аренды."""

from django import forms
from django.utils import timezone

from web_bikes.models import Bike, Station

from .models import Rental, User

DEFAULT_SORT = "date"

STATUS_CHOICES = (("all", "Все аренды"),) + tuple(Rental.Status.choices)

SORT_CHOICES = (
    ("date", "Дате (сначала новые)"),
    ("date_asc", "Дате (сначала старые)"),
    ("bike", "Велосипеду"),
    ("user", "Клиенту"),
    ("station", "Станции"),
)


class RentalFilterForm(forms.Form):
    """Форма поиска, фильтрации и сортировки списка аренд."""

    search = forms.CharField(
        required=False,
        label="Поиск",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Модель, клиент, email или станция",
            }
        ),
    )

    status = forms.ChoiceField(
        required=False,
        label="Статус",
        choices=STATUS_CHOICES,
        initial="all",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    bike = forms.ModelChoiceField(
        required=False,
        label="Велосипед",
        queryset=Bike.objects.order_by("model"),
        empty_label="Все велосипеды",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    user = forms.ModelChoiceField(
        required=False,
        label="Клиент",
        queryset=User.objects.order_by("name"),
        empty_label="Все клиенты",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    station = forms.ModelChoiceField(
        required=False,
        label="Станция",
        queryset=Station.objects.order_by("name"),
        empty_label="Все станции",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    sort = forms.ChoiceField(
        required=False,
        label="Сортировка",
        choices=SORT_CHOICES,
        initial=DEFAULT_SORT,
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class RentalForm(forms.ModelForm):
    """Создание и редактирование аренды велосипеда."""

    start_time = forms.DateTimeField(
        label="Время начала",
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=(
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        ),
        help_text="Дата и время выдачи велосипеда клиенту.",
    )

    class Meta:
        model = Rental
        fields = ("bike", "user", "station", "start_time")
        widgets = {
            "bike": forms.Select(attrs={"class": "form-select"}),
            "user": forms.Select(attrs={"class": "form-select"}),
            "station": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "bike": "Велосипед",
            "user": "Клиент",
            "station": "Станция",
        }
        help_texts = {
            "bike": (
                "Велосипед должен быть свободен: занятые велосипеды "
                "форма отклонит."
            ),
            "station": "Станция, на которой клиент получает велосипед.",
        }

    def clean_start_time(self):
        """Запретить создание новой аренды с датой в прошлом."""
        start_time = self.cleaned_data["start_time"]

        if (
            self.instance._state.adding
            and timezone.localdate(start_time) < timezone.localdate()
        ):
            raise forms.ValidationError(
                "Дата начала аренды не может быть в прошлом.",
                code="start_time_in_past",
            )

        return start_time

    def clean(self):
        """Проверить, что на станции есть свободные места."""
        cleaned_data = super().clean()
        station = cleaned_data.get("station")

        if station is None:
            return cleaned_data

        active_at_station = (
            Rental.objects.active()
            .filter(station=station)
            .exclude(pk=self.instance.pk)
            .count()
        )

        if active_at_station >= station.capacity:
            self.add_error(
                "station",
                (
                    f"На станции «{station.name}» нет свободных мест: "
                    f"активных аренд {active_at_station} из "
                    f"{station.capacity}."
                ),
            )

        return cleaned_data
