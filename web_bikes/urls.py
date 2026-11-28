from django.urls import path

from . import views

app_name = "web_bikes"

urlpatterns = [
    path("", views.bikes_list_view, name="list"),
    path("create/", views.bike_create_view, name="create"),
    path("<slug:slug>/edit/", views.bike_update_view, name="edit"),
    path("<slug:slug>/", views.bike_detail_view, name="detail"),
]

