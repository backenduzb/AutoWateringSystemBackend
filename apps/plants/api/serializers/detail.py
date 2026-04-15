from rest_framework import serializers
from apps.plants.models import PlantProfile, ControlConfig


class PlantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantProfile
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "description",
            "ideal_soil_moisture_min",
            "ideal_soil_moisture_max",
            "watering_note",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ControlConfigSerializer(serializers.ModelSerializer):
    selected_plant = PlantProfileSerializer(read_only=True)
    selected_plant_id = serializers.PrimaryKeyRelatedField(
        queryset=PlantProfile.objects.filter(is_active=True),
        source="selected_plant",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ControlConfig
        fields = [
            "id",
            "selected_plant",
            "selected_plant_id",
            "auto_mode",
            "manual_override",
            "motor_enabled",
            "updated_at",
        ]