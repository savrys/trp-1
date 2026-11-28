from django.urls import path

from . import views

app_name = "web_rentals"

urlpatterns = [
    path("", views.rentals_list_view, name="list"),
    path("statistics/", views.rental_statistics_view, name="statistics"),
    path("create/", views.rental_create_view, name="create"),
    path(
        "<int:rental_id>/edit/",
        views.rental_update_view,
        name="edit",
    ),
    path(
        "<int:rental_id>/cancel/",
        views.rental_cancel_view,
        name="cancel",
    ),
    path("<int:rental_id>/", views.rental_detail_view, name="detail"),
    path(
        "<int:rental_id>/complete/",
        views.rental_complete_view,
        name="complete",
    ),
]

