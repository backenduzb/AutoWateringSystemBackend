from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.plants.models import PlantProfile, ControlConfig
from apps.plants.api.serializers.detail import PlantProfileSerializer, ControlConfigSerializer


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
        return Response(serializer.data, status=status.HTTP_200_OK)