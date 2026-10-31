from django.shortcuts import render

from db.repository import get_all_stations


def index(request):
    stations = get_all_stations()

    return render(
        request,
        "web_main/index.html",
        {"stations": stations},
    )