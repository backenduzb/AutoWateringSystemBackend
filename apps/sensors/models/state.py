from django.db import models

class SystemState(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=100, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}={self.value}"