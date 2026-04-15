from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path("ws/updates/", consumers.UpdatesConsumer.as_asgi()),
    path("ws/sensors/", consumers.SensorConsumer.as_asgi()),  
]