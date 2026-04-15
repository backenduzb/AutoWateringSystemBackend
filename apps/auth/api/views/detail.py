from rest_framework.response import Response
from rest_framework.views import APIView
from common.drfu.permissions import IsAuthenticated
from apps.auth.api.serializers.detail import UserSerializer

class GetMeView(APIView):
    permission_classes = [IsAuthenticated]
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