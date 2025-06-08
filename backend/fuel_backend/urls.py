from django.urls import path
from . import views

urlpatterns = [
    path("average_price_daily/", views.average_price_daily_view),
]