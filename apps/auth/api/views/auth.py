from rest_framework.response import Response
from rest_framework.views import APIView
from apps.auth.api.serializers.auth import (
    UserRegisterSerializer,
)
from common.drfu.permissions import AllowAny

class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {"message": "User yaratilindi!", "data": serializer.data}, status=201
            )

        return Response(serializer.errors, status=400)