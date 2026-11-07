"""Регистрация моделей велосипедов и станций в админке Django."""

from django.contrib import admin

from .models import Bike, Station


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    """Управление станциями проката."""

    list_display = ("id", "name", "capacity")
    search_fields = ("name",)
    list_filter = ("capacity",)
    ordering = ("name",)


@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    """Управление парком велосипедов."""

    list_display = ("id", "model", "type", "is_available")
    list_filter = ("type", "is_available")
    search_fields = ("model",)
    ordering = ("model",)

