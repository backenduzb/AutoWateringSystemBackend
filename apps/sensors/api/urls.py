from django.urls import path

from .views import LatestHumidityView

urlpatterns = [
    path("latest/", LatestHumidityView.as_view(), name="humidity-latest"),
]