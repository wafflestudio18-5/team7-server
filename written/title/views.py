from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


class TitleViewSet(viewsets.GenericViewSet):
    def list(self, request):
        return Response(status=status.HTTP_200_OK)
