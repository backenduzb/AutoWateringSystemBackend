from __future__ import annotations

import json
from datetime import datetime
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from apps.sensors.models import HumidityReading

GROUP_UPDATES = "humidity_updates"
GROUP_DEVICES = "esp32_devices"

_motor_state = {"value": False}


def get_motor_state() -> bool:
    return _motor_state["value"]


def set_motor_state(value: bool) -> bool:
    _motor_state["value"] = value
    return value


def get_device_tokens() -> set[str]:
    return set(getattr(settings, "TELEMETRY_DEVICE_TOKENS", []))


def is_valid_device(secret: str | None) -> bool:
    return bool(secret and secret in get_device_tokens())


@sync_to_async
def create_reading(value: float, source: str):
    return HumidityReading.objects.create(value=value, source=source)


@sync_to_async
def get_latest_reading_payload():
    latest = HumidityReading.objects.order_by("-created_at").first()
    if not latest:
        return {
            "type": "reading",
            "data": {
                "value": None,
                "source": None,
                "timestamp": None,
            },
            "motor_state": get_motor_state(),
        }

    return {
        "type": "reading",
        "data": {
            "value": latest.value,
            "source": latest.source,
            "timestamp": latest.created_at.isoformat(),
        },
        "motor_state": get_motor_state(),
    }


class UpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not getattr(user, "is_authenticated", False):
            await self.close(code=4401)
            return

        await self.channel_layer.group_add(GROUP_UPDATES, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps(await get_latest_reading_payload()))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(GROUP_UPDATES, self.channel_name)

    async def humidity_reading(self, event):
        await self.send(text_data=json.dumps(event["payload"]))

    async def motor_state_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "motor_state",
                    "motor_state": event["motor_state"],
                    "timestamp": event["timestamp"],
                }
            )
        )


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query = parse_qs(self.scope.get("query_string", b"").decode())
        secret = query.get("secret", [None])[0]

        if not is_valid_device(secret):
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(GROUP_DEVICES, self.channel_name)
        await self.accept()
        await self.send_current_motor_state()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(GROUP_DEVICES, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": "invalid_json",
                    }
                )
            )
            return

        msg_type = payload.get("type")

        if msg_type == "request_motor_state":
            await self.send_current_motor_state()
            return

        if msg_type == "motor_command":
            command = str(payload.get("command", "")).upper()
            if command not in {"ON", "OFF"}:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "error",
                            "message": "invalid_command",
                            "valid_commands": ["ON", "OFF"],
                        }
                    )
                )
                return

            new_state = command == "ON"
            set_motor_state(new_state)
            await self.broadcast_motor_state(new_state)

            await self.send(
                text_data=json.dumps(
                    {
                        "type": "ack",
                        "command": command,
                        "motor_state": new_state,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            )
            return

        raw_value = payload.get("value", payload.get("humidity"))
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": "value_must_be_numeric",
                    }
                )
            )
            return

        source = (self.scope.get("client") or ["esp32"])[0]
        reading = await create_reading(value=value, source=source)

        out = {
            "type": "reading",
            "data": {
                "value": reading.value,
                "source": reading.source,
                "timestamp": reading.created_at.isoformat(),
            },
            "motor_state": get_motor_state(),
        }

        await self.channel_layer.group_send(
            GROUP_UPDATES,
            {
                "type": "humidity_reading",
                "payload": out,
            },
        )

        await self.send(
            text_data=json.dumps(
                {
                    "type": "ack",
                    "status": "ok",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        )

    async def motor_command_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "motor_command",
                    "command": event["command"],
                    "motor_state": event["motor_state"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def send_current_motor_state(self):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "motor_state",
                    "motor_state": get_motor_state(),
                    "timestamp": datetime.now().isoformat(),
                }
            )
        )

    async def broadcast_motor_state(self, state: bool):
        timestamp = datetime.now().isoformat()

        await self.channel_layer.group_send(
            GROUP_UPDATES,
            {
                "type": "motor_state_message",
                "motor_state": state,
                "timestamp": timestamp,
            },
        )

        await self.channel_layer.group_send(
            GROUP_DEVICES,
            {
                "type": "motor_command_message",
                "command": "ON" if state else "OFF",
                "motor_state": state,
                "timestamp": timestamp,
            },
        )


class MotorControlConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        is_user = bool(user and getattr(user, "is_authenticated", False))

        query = parse_qs(self.scope.get("query_string", b"").decode())
        secret = query.get("secret", [None])[0]
        is_device = is_valid_device(secret)

        if not is_user and not is_device:
            await self.close(code=4401)
            return

        if is_device:
            await self.channel_layer.group_add(GROUP_DEVICES, self.channel_name)

        await self.accept()
        await self.send(
            text_data=json.dumps(
                {
                    "type": "motor_state",
                    "motor_state": get_motor_state(),
                    "timestamp": datetime.now().isoformat(),
                }
            )
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(GROUP_DEVICES, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
    
        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": "invalid_json",
                    }
                )
            )
            return
    
        if payload.get("type") == "motor_applied":
            applied_state = bool(payload.get("motor_state", False))
            set_motor_state(applied_state)
            timestamp = datetime.now().isoformat()
    
            await self.channel_layer.group_send(
                GROUP_UPDATES,
                {
                    "type": "motor_state_message",
                    "motor_state": applied_state,
                    "timestamp": timestamp,
                },
            )
    
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "ack",
                        "motor_state": applied_state,
                        "timestamp": timestamp,
                    }
                )
            )
            return
    
        if payload.get("type") == "request_motor_state":
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "motor_state",
                        "motor_state": get_motor_state(),
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            )
            return
    
        command = str(payload.get("command", "")).upper()
        if command not in {"ON", "OFF"}:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": "invalid_command",
                    }
                )
            )
            return
    
        new_state = command == "ON"
        set_motor_state(new_state)
        timestamp = datetime.now().isoformat()
    
        await self.channel_layer.group_send(
            GROUP_DEVICES,
            {
                "type": "motor_command_message",
                "command": command,
                "motor_state": new_state,
                "timestamp": timestamp,
            },
        )
    
        await self.channel_layer.group_send(
            GROUP_UPDATES,
            {
                "type": "motor_state_message",
                "motor_state": new_state,
                "timestamp": timestamp,
            },
        )
    
        await self.send(
            text_data=json.dumps(
                {
                    "type": "ack",
                    "command": command,
                    "motor_state": new_state,
                    "timestamp": timestamp,
                }
            )
        )