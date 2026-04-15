from __future__ import annotations

import json
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

from apps.sensors.models import HumidityReading


GROUP_NAME = "humidity"


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
        await self.send(text_data=json.dumps(await _get_latest_payload()))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(GROUP_NAME, self.channel_name)

    async def humidity_reading(self, event):
        await self.send(text_data=json.dumps(event["payload"]))


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query = parse_qs(self.scope.get("query_string", b"").decode("utf-8"))
        secret = query.get("secret", [None])[0]
        allowed = set(getattr(settings, "TELEMETRY_DEVICE_TOKENS", []))
        if not secret or secret not in allowed:
            await self.close(code=4403)
            return

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "invalid json"}))
            return

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
