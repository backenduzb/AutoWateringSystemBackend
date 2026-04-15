from django.db import models


class PlantProfile(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=80, blank=True, default="")
    description = models.TextField(blank=True, default="")
    ideal_soil_moisture_min = models.FloatField()
    ideal_soil_moisture_max = models.FloatField()
    watering_note = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ControlConfig(models.Model):
    selected_plant = models.ForeignKey(
        PlantProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="control_configs",
    )
    auto_mode = models.BooleanField(default=True)
    manual_override = models.BooleanField(default=False)
    motor_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ControlConfig #{self.pk}"