from rest_framework.response import Response
from rest_framework.views import APIView
from common.drfu.permissions import IsAuthenticated

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

