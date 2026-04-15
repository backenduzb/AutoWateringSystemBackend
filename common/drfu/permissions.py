from rest_framework.permissions import BasePermission, IsAuthenticated, AllowAny

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff