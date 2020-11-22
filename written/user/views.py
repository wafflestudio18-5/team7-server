from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

class UserViewSet(viewsets.GenericViewSet):
    def create(selfs, request):
        return Response(status=status.HTTP_200_OK)

    def login(self, request):
        return Response(status=status.HTTP_200_OK)

    def logout(self, request):
        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request):
        return Response(status=status.HTTP_200_OK)

    def update(self, request):
        return Response(status=status.HTTP_200_OK)