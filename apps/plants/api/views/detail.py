from apps.plants.api.serializers.detail import (
    ControlConfigSerializer,
    PlantProfileSerializer,
)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.plants.models import ControlConfig, PlantProfile
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.sensors.models import SystemState

class PlantListCreateView(generics.ListCreateAPIView):
    queryset = PlantProfile.objects.all()
    serializer_class = PlantProfileSerializer
    permission_classes = [IsAuthenticated]


class PlantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlantProfile.objects.all()
    serializer_class = PlantProfileSerializer
    permission_classes = [IsAuthenticated]



class ControlConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, _ = ControlConfig.objects.get_or_create(
            pk=1,
            defaults={
                "auto_mode": True,
                "manual_override": False,
                "motor_enabled": True,
            },
        )
        return obj

    def get(self, request):
        serializer = ControlConfigSerializer(self.get_object())
        return Response(serializer.data)

    def patch(self, request):
        obj = self.get_object()
        serializer = ControlConfigSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        auto_mode = serializer.instance.auto_mode

        if auto_mode is False:
            state_obj, _ = SystemState.objects.get_or_create(
                key="motor_state",
                defaults={"value": "false"},
            )
            state_obj.value = "false"
            state_obj.save(update_fields=["value", "updated_at"])

            channel_layer = get_channel_layer()

            async_to_sync(channel_layer.group_send)(
                "humidity_updates",
                {
                    "type": "motor_state_message",
                    "motor_state": False,
                    "timestamp": serializer.instance.updated_at.isoformat(),
                },
            )

            async_to_sync(channel_layer.group_send)(
                "esp32_devices",
                {
                    "type": "motor_command_message",
                    "command": "OFF",
                    "motor_state": False,
                    "timestamp": serializer.instance.updated_at.isoformat(),
                },
            )

        return Response(ControlConfigSerializer(serializer.instance).data, status=status.HTTP_200_OK)