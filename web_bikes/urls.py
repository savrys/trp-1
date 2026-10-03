from django.urls import path
from . import views

urlpatterns = [
    path('', views.bikes_list_view, name='bikes_list'),
    path('<int:bike_id>/', views.bike_detail_view, name='bike_detail'),
]
