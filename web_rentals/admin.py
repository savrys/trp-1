"""Регистрация моделей клиентов и аренд в админке Django."""

from django.contrib import admin, messages

from web_bikes.models import Bike

from .models import Rental, User


class UserRentalInline(admin.TabularInline):
    """Аренды клиента в его карточке."""

    model = Rental
    fields = ("id", "bike", "station", "start_time", "status")
    readonly_fields = ("id",)
    autocomplete_fields = ("bike", "station")
    extra = 0
    show_change_link = True
    ordering = ("-start_time",)
    verbose_name = "Аренда клиента"
    verbose_name_plural = "Аренды клиента"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Управление клиентами сервиса."""

    list_display = (
        "id",
        "name",
        "email",
        "rentals_total_count",
        "rentals_active_count",
    )
    list_display_links = ("id", "name")
    search_fields = ("name", "email")
    ordering = ("name",)
    list_per_page = 10
    save_on_top = True
    readonly_fields = (
        "id",
        "rentals_total_count",
        "rentals_active_count",
    )
    fieldsets = (
        (
            "Контактные данные",
            {
                "fields": ("id", "name", "email"),
                "description": "Электронная почта клиента должна быть уникальной.",
            },
        ),
        (
            "Статистика аренд",
            {
                "fields": ("rentals_total_count", "rentals_active_count"),
                "classes": ("collapse",),
                "description": "Показатели вычисляются ORM-аннотацией.",
            },
        ),
    )
    inlines = (UserRentalInline,)

    def get_queryset(self, request):
        """Дополнить список клиентов статистикой аренд без N+1."""
        return super().get_queryset(request).with_rental_stats()

    @admin.display(description="Всего аренд", ordering="rentals_total")
    def rentals_total_count(self, obj):
        """Количество всех аренд клиента."""
        return obj.rentals_total

    @admin.display(description="Активных аренд", ordering="rentals_active")
    def rentals_active_count(self, obj):
        """Количество активных аренд клиента."""
        return obj.rentals_active


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    """Управление арендами велосипедов."""

    list_display = (
        "id",
        "bike",
        "bike_type",
        "user",
        "station",
        "start_time",
        "status",
        "is_active_display",
    )
    list_display_links = ("id", "bike")
    list_editable = ("status",)
    list_filter = ("status", "station", "bike__type")
    search_fields = ("bike__model", "user__name", "user__email", "station__name")
    autocomplete_fields = ("bike", "user", "station")
    date_hierarchy = "start_time"
    list_select_related = ("bike", "user", "station")
    ordering = ("-start_time", "pk")
    list_per_page = 20
    save_on_top = True
    actions = ("complete_rentals", "cancel_rentals", "restore_rentals")
    readonly_fields = ("id", "is_active_display")
    fieldsets = (
        (
            "Участники аренды",
            {
                "fields": ("id", "bike", "user", "station"),
                "description": (
                    "Поля связанных моделей подгружаются автодополнением "
                    "и через select_related без лишних запросов."
                ),
            },
        ),
        (
            "Период и статус",
            {
                "fields": ("start_time", "status", "is_active_display"),
                "description": "Статус можно менять прямо в списке аренд.",
            },
        ),
    )

    @admin.display(description="Тип велосипеда", ordering="bike__type")
    def bike_type(self, obj):
        """Тип велосипеда из связанной модели."""
        return obj.bike.get_type_display()

    @admin.display(boolean=True, description="Активна")
    def is_active_display(self, obj):
        """Логический признак активной аренды."""
        return obj.is_active

    @admin.action(description="Завершить выбранные аренды")
    def complete_rentals(self, request, queryset):
        """Завершить активные аренды и вернуть велосипеды в парк."""
        active = queryset.active()
        bike_ids = list(active.values_list("bike_id", flat=True))

        if not bike_ids:
            self.message_user(
                request,
                "Среди выбранных записей нет активных аренд.",
                messages.WARNING,
            )
            return

        updated = active.update(status=Rental.Status.COMPLETED)
        Bike.objects.filter(pk__in=bike_ids).update(is_available=True)

        self.message_user(
            request,
            f"Завершено аренд: {updated}. Велосипеды возвращены в парк.",
        )

    @admin.action(description="Отменить выбранные аренды")
    def cancel_rentals(self, request, queryset):
        """Отменить активные аренды и вернуть велосипеды в парк."""
        active = queryset.active()
        bike_ids = list(active.values_list("bike_id", flat=True))

        if not bike_ids:
            self.message_user(
                request,
                "Среди выбранных записей нет активных аренд.",
                messages.WARNING,
            )
            return

        updated = active.update(status=Rental.Status.CANCELLED)
        Bike.objects.filter(pk__in=bike_ids).update(is_available=True)

        self.message_user(
            request,
            f"Отменено аренд: {updated}. Велосипеды возвращены в парк.",
        )

    @admin.action(description="Вернуть выбранные аренды в работу")
    def restore_rentals(self, request, queryset):
        """Снова сделать завершённые и отменённые аренды активными."""
        inactive = queryset.exclude(status=Rental.Status.ACTIVE)
        bike_ids = list(inactive.values_list("bike_id", flat=True))

        if not bike_ids:
            self.message_user(
                request,
                "Все выбранные аренды уже активны.",
                messages.WARNING,
            )
            return

        updated = inactive.update(status=Rental.Status.ACTIVE)
        Bike.objects.filter(pk__in=bike_ids).update(is_available=False)

        self.message_user(
            request,
            f"Возвращено в работу аренд: {updated}.",
        )

    def get_queryset(self, request):
        """Дополнить список аренд связанными объектами."""
        return super().get_queryset(request).with_related()
