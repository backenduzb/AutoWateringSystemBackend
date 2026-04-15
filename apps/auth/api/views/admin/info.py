from rest_framework import filters, viewsets
from common.drfu import permissions
from apps.auth.models import User
from apps.auth.api.serializers.admin.auth import  UserAdminSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from common.drfu.permissions import IsAdmin
from apps.auth.api.serializers.detail import UserSerializer

class GetMeView(APIView):
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response({'data': serializer.data}, status=200)

    def patch(self, request):
        serializer = self.serializer_class(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({'data': serializer.data}, status=200)
         
        return Response(serializer.errors, status=400)
        

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserAdminSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "middle_name",
    ]
