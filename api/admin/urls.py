from django.urls import path, include

urlpatterns = [
    path("accounts/", include("apps.auth.api.admin")),
]
