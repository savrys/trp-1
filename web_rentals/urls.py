from django.urls import path
from . import views

urlpatterns = [
    path('', views.rentals_list_view, name='rentals_list'),
    path('<int:rental_id>/', views.rental_detail_view, name='rental_detail'),
]
