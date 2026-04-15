from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/updates/$', consumers.UpdatesConsumer.as_asgi()),
    
    re_path(r'ws/sensors/$', consumers.SensorConsumer.as_asgi()),
    
    re_path(r'ws/motor/control/$', consumers.MotorControlConsumer.as_asgi()),
    
    re_path(r'ws/esp32/commands/$', consumers.ESP32CommandConsumer.as_asgi()),
]