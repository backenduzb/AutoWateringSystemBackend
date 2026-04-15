from django.urls import path

from .views import LatestHumidityView
from . import views

urlpatterns = [
    path('motor/control/', views.control_motor, name='control_motor'),
    path('motor/status/', views.get_motor_status, name='get_motor_status'),
    path("latest/", LatestHumidityView.as_view(), name="humidity-latest"),
]