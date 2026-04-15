from rest_framework.routers import DefaultRouter
from apps.auth.api.views.admin.info import UserViewSet
from .views.admin.auth import AdminAuthenticateView, AdminRefreshView
from .views.detail import GetMeView
from django.urls import path, include

router = DefaultRouter()

router.register(r"users", UserViewSet, basename="admin-users")

urlpatterns = [
    path("", include(router.urls)),
    path("token/", AdminAuthenticateView.as_view(), name="admin-authenticate"),
    path("refresh/", AdminRefreshView.as_view(), name="admin-refresh"),
    path("me/", GetMeView.as_view(), name="admin-me")
]