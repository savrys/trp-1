"""Регистрация моделей велосипедов и станций в админке Django."""

from django.contrib import admin

from web_rentals.models import Rental

from .models import Bike, Station


class BikeRentalInline(admin.TabularInline):
    """История аренд в карточке велосипеда."""

    model = Rental
    fields = ("id", "user", "station", "start_time", "status")
    readonly_fields = ("id",)
    autocomplete_fields = ("user", "station")
    extra = 0
    can_delete = False
    show_change_link = True
    ordering = ("-start_time",)
    verbose_name = "Аренда велосипеда"
    verbose_name_plural = "История аренды"


class StationRentalInline(admin.TabularInline):
    """Аренды, оформленные на станции."""

    model = Rental
    fields = ("id", "user", "bike", "start_time", "status")
    readonly_fields = ("id",)
    autocomplete_fields = ("user", "bike")
    extra = 0
    can_delete = False
    show_change_link = True
    ordering = ("-start_time",)
    verbose_name = "Аренда станции"
    verbose_name_plural = "Аренды станции"


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    """Управление станциями проката."""

    list_display = (
        "id",
        "name",
        "capacity",
        "is_large",
        "rentals_total_count",
        "rentals_active_count",
    )
    list_display_links = ("id", "name")
    list_editable = ("capacity",)
    list_filter = ("is_large",)
    search_fields = ("name",)
    ordering = ("name",)
    list_per_page = 10
    save_on_top = True
    readonly_fields = (
        "id",
        "is_large",
        "rentals_total_count",
        "rentals_active_count",
    )
    fieldsets = (
        (
            "Основные сведения",
            {
                "fields": ("id", "name", "capacity"),
                "description": (
                    "Название и вместимость станции. "
                    "Вместимость можно изменить прямо в списке станций."
                ),
            },
        ),
        (
            "Вычисляемые показатели",
            {
                "fields": (
                    "is_large",
                    "rentals_total_count",
                    "rentals_active_count",
                ),
                "classes": ("collapse",),
                "description": (
                    "Поле «Крупная станция» рассчитывает сама база данных. "
                    "Количество аренд вычисляется ORM-аннотацией."
                ),
            },
        ),
    )
    inlines = (StationRentalInline,)

    def get_queryset(self, request):
        """Дополнить список станций статистикой аренд без N+1."""
        return super().get_queryset(request).with_rental_stats()

    @admin.display(description="Всего аренд", ordering="rentals_total")
    def rentals_total_count(self, obj):
        """Количество всех аренд станции."""
        return obj.rentals_total

    @admin.display(description="Активных аренд", ordering="rentals_active")
    def rentals_active_count(self, obj):
        """Количество активных аренд станции."""
        return obj.rentals_active


@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    """Управление парком велосипедов."""

    list_display = (
        "id",
        "model",
        "type",
        "is_available",
        "slug",
        "rentals_total_count",
        "rentals_active_count",
    )
    list_display_links = ("id", "model")
    list_editable = ("is_available",)
    list_filter = ("type", "is_available")
    search_fields = ("model", "slug")
    ordering = ("model",)
    list_per_page = 10
    save_on_top = True
    readonly_fields = (
        "id",
        "slug",
        "rentals_total_count",
        "rentals_active_count",
    )
    fieldsets = (
        (
            "Характеристики",
            {
                "fields": (
                    "id",
                    "model",
                    "type",
                    "is_available",
                    "image",
                ),
                "description": (
                    "Доступность можно переключать прямо в списке велосипедов. "
                    "Изображение загружается в формате JPEG, PNG или WebP."
                ),
            },
        ),
        (
            "Адрес и статистика",
            {
                "fields": (
                    "slug",
                    "rentals_total_count",
                    "rentals_active_count",
                ),
                "classes": ("collapse",),
                "description": (
                    "Slug формируется автоматически при первом сохранении "
                    "и используется в адресе подробной страницы."
                ),
            },
        ),
    )
    inlines = (BikeRentalInline,)

    def get_queryset(self, request):
        """Дополнить список велосипедов статистикой аренд без N+1."""
        return super().get_queryset(request).with_rental_stats()

    def view_on_site(self, obj):
        """Открывать из админки публичную страницу по slug."""
        return obj.get_absolute_url()

    @admin.display(description="Всего аренд", ordering="rentals_total")
    def rentals_total_count(self, obj):
        """Количество всех аренд велосипеда."""
        return obj.rentals_total

    @admin.display(description="Активных аренд", ordering="rentals_active")
    def rentals_active_count(self, obj):
        """Количество активных аренд велосипеда."""
        return obj.rentals_active
