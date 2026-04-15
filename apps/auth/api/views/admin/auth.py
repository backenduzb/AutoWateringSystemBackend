from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.auth.api.serializers.admin.auth import (
    AdminTokenObtainPairSerializer, TokenRefreshSerializer
)
from common.drfu.permissions import AllowAny

class AdminAuthenticateView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = AdminTokenObtainPairSerializer
    
class AdminRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    serializer_class = TokenRefreshSerializer
