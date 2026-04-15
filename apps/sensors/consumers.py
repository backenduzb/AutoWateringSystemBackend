from __future__ import annotations

import json
from urllib.parse import parse_qs
from datetime import datetime

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.conf import settings

from apps.sensors.models import HumidityReading

GROUP_NAME = "humidity"
ESP32_GROUP_NAME = "esp32_devices"

_motor_state = {"state": False}

def get_motor_state():
    return _motor_state["state"]

def set_motor_state(state: bool):
    _motor_state["state"] = state
    return state


@sync_to_async
def _create_reading(value: float, source: str) -> HumidityReading:
    return HumidityReading.objects.create(value=value, source=source)


@sync_to_async
def _get_latest_payload():
    latest = HumidityReading.objects.order_by("-created_at").first()
    if not latest:
        return {"type": "reading", "data": {"value": None, "source": None, "timestamp": None}}
    return {
        "type": "reading",
        "data": {
            "value": latest.value,
            "source": latest.source,
            "timestamp": latest.created_at.isoformat(),
        },
    }


class UpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not getattr(user, "is_authenticated", False):
            await self.close(code=4401)
            return

        await self.accept()
        await self.channel_layer.group_add(GROUP_NAME, self.channel_name)
        
        payload = await _get_latest_payload()
        payload["motor_state"] = get_motor_state()
        
        await self.send(text_data=json.dumps(payload))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(GROUP_NAME, self.channel_name)

    async def humidity_reading(self, event):
        event["payload"]["motor_state"] = get_motor_state()
        await self.send(text_data=json.dumps(event["payload"]))
    
    async def motor_state_update(self, event):
        """Motor state yangilanishini web dashboardga yuborish"""
        await self.send(text_data=json.dumps({
            "type": "motor_state",
            "motor_state": event["state"],
            "timestamp": event.get("timestamp", datetime.now().isoformat())
        }))


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query = parse_qs(self.scope.get("query_string", b"").decode("utf-8"))
        secret = query.get("secret", [None])[0]
        allowed = set(getattr(settings, "TELEMETRY_DEVICE_TOKENS", []))
        
        if not secret or secret not in allowed:
            await self.close(code=4403)
            return

        await self.accept()
        await self.channel_layer.group_add(ESP32_GROUP_NAME, self.channel_name)
        
        # ESP32 ga joriy motor holatini yuborish
        await self.send(text_data=json.dumps({
            "type": "motor_state",
            "state": get_motor_state()
        }))

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "invalid json"}))
            return
            
        # Motor commandni qabul qilish (ESP32 dan kelishi mumkin)
        if payload.get("type") == "motor_command":
            command = payload.get("command", "").upper()
            if command == "ON":
                set_motor_state(True)
                await self._broadcast_motor_state(True)
                await self.send(text_data=json.dumps({
                    "status": "ok",
                    "motor_state": True,
                    "message": "Motor turned ON"
                }))
            elif command == "OFF":
                set_motor_state(False)
                await self._broadcast_motor_state(False)
                await self.send(text_data=json.dumps({
                    "status": "ok",
                    "motor_state": False,
                    "message": "Motor turned OFF"
                }))
            else:
                await self.send(text_data=json.dumps({
                    "error": "invalid command",
                    "valid_commands": ["ON", "OFF"]
                }))
            return

        # Sensor ma'lumotlarini qabul qilish
        raw = payload.get("value", payload.get("humidity"))
        try:
            value = float(raw)
        except (TypeError, ValueError):
            await self.send(text_data=json.dumps({"error": "value must be numeric"}))
            return

        source = (self.scope.get("client") or ["esp32"])[0]
        reading = await _create_reading(value=value, source=source)
        
        out = {
            "type": "reading",
            "data": {
                "value": reading.value,
                "source": reading.source,
                "timestamp": reading.created_at.isoformat(),
            },
        }

        await self.channel_layer.group_send(
            GROUP_NAME,
            {"type": "humidity.reading", "payload": out},
        )
        
        await self.send(text_data=json.dumps({"status": "ok"}))

    async def _broadcast_motor_state(self, state: bool):
        """Motor holatini barcha mijozlarga yuborish"""
        # Web dashboard uchun
        await self.channel_layer.group_send(
            GROUP_NAME,
            {
                "type": "motor_state_update",
                "state": state,
                "timestamp": datetime.now().isoformat()
            },
        )
        
        # ESP32 uchun
        await self.channel_layer.group_send(
            ESP32_GROUP_NAME,
            {
                "type": "motor_command_to_esp32",
                "command": "ON" if state else "OFF",
                "state": state
            },
        )

    async def motor_command_to_esp32(self, event):
        """ESP32 ga motor command yuborish"""
        await self.send(text_data=json.dumps({
            "type": "motor_command",
            "command": event["command"],
            "state": event["state"]
        }))


class MotorControlConsumer(AsyncWebsocketConsumer):
    """Web client to ESP32 motor control (Dashboard dan boshqarish)"""
    
    async def connect(self):
        user = self.scope.get("user")
        if not user or not getattr(user, "is_authenticated", False):
            await self.close(code=4401)
            return

        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "invalid json"}))
            return

        command = payload.get("command", "").upper()
        
        if command not in ["ON", "OFF"]:
            await self.send(text_data=json.dumps({"error": "invalid command"}))
            return

        new_state = command == "ON"
        set_motor_state(new_state)
        
        # ESP32 guruhiga komanda yuborish
        await self.channel_layer.group_send(
            ESP32_GROUP_NAME,
            {
                "type": "motor_command_to_esp32",
                "command": command,
                "state": new_state
            }
        )
        
        # Web dashboardga yangilanish yuborish
        await self.channel_layer.group_send(
            GROUP_NAME,
            {
                "type": "motor_state_update",
                "state": new_state,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        await self.send(text_data=json.dumps({
            "status": "ok",
            "command": command,
            "motor_state": new_state
        }))