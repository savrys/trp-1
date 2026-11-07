"""Регистрация моделей клиентов и аренд в админке Django."""

from django.contrib import admin

from .models import Rental, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Управление клиентами сервиса."""

    list_display = ("id", "name", "email")
    search_fields = ("name", "email")
    ordering = ("name",)


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    """Управление арендами велосипедов."""

    list_display = (
        "id",
        "bike",
        "user",
        "station",
        "start_time",
        "is_completed",
    )
    list_filter = ("is_completed", "station", "bike__type")
    search_fields = ("bike__model", "user__name", "user__email")
    list_select_related = ("bike", "user", "station")
    date_hierarchy = "start_time"
    ordering = ("-start_time",)

