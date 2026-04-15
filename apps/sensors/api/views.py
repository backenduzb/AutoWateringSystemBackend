from rest_framework.response import Response
from rest_framework.views import APIView
from common.drfu.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from ..consumers import get_motor_state, set_motor_state
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from datetime import datetime
from apps.sensors.models import HumidityReading


class LatestHumidityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latest = HumidityReading.objects.order_by("-created_at").first()
        if not latest:
            return Response({"data": {"value": None, "source": None, "timestamp": None}}, status=200)

        return Response(
            {
                "data": {
                    "value": latest.value,
                    "source": latest.source,
                    "timestamp": latest.created_at.isoformat(),
                }
            },
            status=200,
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def control_motor(request):
    """
    Motor state ni REST API orqali boshqarish
    """
    try:
        state = request.data.get('state')
        
        if state is None:
            return Response(
                {'error': 'state parameter required (true/false)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Boolean ga o'tkazish
        if isinstance(state, str):
            state = state.lower() == 'true'
        else:
            state = bool(state)
        
        # Motor holatini o'zgartirish
        set_motor_state(state)
        
        # WebSocket orqali barcha mijozlarga xabar yuborish
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "humidity",
            {
                "type": "motor_state_update",
                "state": state,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # ESP32 ga komanda yuborish
        async_to_sync(channel_layer.group_send)(
            "esp32_devices",
            {
                "type": "motor_command_to_esp32",
                "command": "ON" if state else "OFF",
                "state": state
            }
        )
        
        return Response({
            'status': 'success',
            'motor_state': state,
            'message': f'Motor turned {"ON" if state else "OFF"}'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_motor_status(request):
    """
    Motor state ni o'qish
    """
    return Response({
        'motor_state': get_motor_state()
    }, status=status.HTTP_200_OK)
