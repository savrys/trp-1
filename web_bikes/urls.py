
from django.urls import path
from . import views

app_name = "web_bikes"

urlpatterns = [
    path("", views.bikes_list_view, name="list"),
    path("<int:bike_id>/", views.bike_detail_view, name="detail"),
]
