from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web_main.urls')),
    path('bikes/', include('web_bikes.urls')),
    path('rentals/', include('web_rentals.urls')),
]
