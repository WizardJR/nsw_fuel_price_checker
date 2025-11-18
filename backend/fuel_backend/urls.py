from django.urls import path
from . import views

urlpatterns = [
    path("average_price_daily/", views.average_price_daily_view),
    path("average_price_predict/", views.average_predict_view),
    path("nearby_stations/", views.nearby_stations),
]