from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path("admin/", include("api.admin.urls")),
    path("accounts/", include("apps.auth.api.urls")),
    path("sensors/", include("apps.sensors.api.urls")),
    path("plants/", include("apps.plants.api.urls")),
]
