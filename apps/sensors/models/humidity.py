from django.db import models


class HumidityReading(models.Model):
    value = models.FloatField()
    source = models.CharField(max_length=128, default="-")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

