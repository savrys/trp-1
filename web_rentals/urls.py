from django.urls import path

from . import views

app_name = "web_rentals"

urlpatterns = [
    path("", views.rentals_list_view, name="list"),
    path("statistics/", views.rental_statistics_view, name="statistics"),
    path("<int:rental_id>/", views.rental_detail_view, name="detail"),
    path(
        "<int:rental_id>/complete/",
        views.rental_complete_view,
        name="complete",
    ),
]

