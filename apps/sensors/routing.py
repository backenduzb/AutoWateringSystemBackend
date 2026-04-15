from django.urls import re_path
from .consumers import UpdatesConsumer, SensorConsumer, MotorControlConsumer

websocket_urlpatterns = [
    re_path(r"^ws/updates/$", UpdatesConsumer.as_asgi()),
    re_path(r"^ws/sensors/$", SensorConsumer.as_asgi()),
    re_path(r"^ws/motor/control/$", MotorControlConsumer.as_asgi()),
]