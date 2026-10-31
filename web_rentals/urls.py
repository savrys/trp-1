
from django.urls import path
from . import views

app_name = "web_rentals"

urlpatterns = [
    path("", views.rentals_list_view, name="list"),
    path(
        "<int:rental_id>/",
        views.rental_detail_view,
        name="detail",
    ),
]
