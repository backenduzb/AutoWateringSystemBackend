from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    middle_name = models.CharField(max_length=128, default="-")
    # Keep a default so `create_superuser(...)` can work without extra fields.
    phone_number = models.CharField(max_length=13, default="-")
