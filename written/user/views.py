from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import IntegrityError
from user.models import UserProfile
from user.serializers import UserSerializer
from rest_framework.authtoken.models import Token
import requests

# API User==================================================================
# POST /users/
# PUT /users/login/
# GET /users/me/
# GET /users/{user_id}/
# PUT /users/me/
# GET /users/{user_id}/postings/

# API Subscription===========================================================
# POST /users/{user_id}/subscribe/
# POST /users/{user_id}/unsubscribe/
# GET /users/subscribed/
# GET /users/subscriber/


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated(), )

    def get_permissions(self):
        if self.action in ('create', 'login'):
            return (AllowAny(), )
        return self.permission_classes

    # API User===============================================================
    # =======================================================================

    def facebook_login(self, data):
        access_token = data.get('access_token')
        nickname = data.get("nickname")
        url = f"https://graph.facebook.com/v7.0/me?access_token={access_token}"
        response = requests.get(url)
        if response.status_code != status.HTTP_200_OK:
            return False
        response_data = response.json()
        if response_data["id"] != data.get("facebookid"):
            return False
        data["username"] = response_data.get("name")
        return True

    def check_nickname(self, data):
        nickname = data.get("nickname")
        if not nickname:
            return False
        if UserProfile.objects.filter(nickname=nickname).count() != 0:
            return False
        return True

    # POST /users/
    def create(self, request):
        if not self.facebook_login(request.data):
            return Response({"errorcode": "10001", "message": "Invalid facebook token"}, status=status.HTTP_400_BAD_REQUEST)
        if not self.check_nickname(request.data):
            return Response({"errorcode": "10002", "message": "Nickname duplicate"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:
            return Response({"errorcode": "10005", "message": "User already signed up"}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        nickname = request.data.get('nickname')
        UserProfile.objects.create(user=user, nickname=nickname, facebook_id=request.data.get('facebookid'))
        data = {'user': serializer.data, 'access_token': user.auth_token.key}

        return Response(data, status=status.HTTP_201_CREATED)

    # PUT /users/login/
    @action(detail=False, methods=['PUT'])
    def login(self, request):
        if not self.facebook_login(request.data):
            return Response({"errorcode": "10001", "message": "Invalid facebook token"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(username=request.data.get("username"))
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        data = {'user': self.get_serializer(user).data, 'access_token': token.key}
        return Response(data, status=status.HTTP_200_OK)

    # GET /users/me/  GET /users/{user_id}/
    def retrieve(self, request, pk=None):
        user = request.user if pk == 'me' else self.get_object()
        return Response(self.get_serializer(user).data)

    # PUT /users/me/
    def update(self, request, pk=None):
        if pk != 'me':
            return Response({"errorcode": "10004", "message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)
        user = request.user
        description = request.data.get('description')
        nickname = request.data.get('nickname')
        if description:
            profile = user.userprofile
            profile.description = description
            profile.save()
        if nickname:
            profile = user.userprofile
            if nickname != profile.nickname and UserProfile.objects.filter(nickname=nickname).count() != 0:
                return Response({"errorcode": "10002", "message": "Nickname duplicate"}, status=status.HTTP_400_BAD_REQUEST)
            profile.nickname = nickname
            profile.save()
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    # GET /users/{user_id}/postings/
    @action(detail=True, methods=['GET'], url_path='postings')
    def postings_of_user(self, request, pk):
        return Response(status=status.HTTP_200_OK)

    # API Subscription===========================================================
    # ===========================================================================
    # POST /users/{user_id}/subscribe/
    @action(detail=True, methods=['POST'], url_path='subscribe')
    def subscribe(self, request, pk):
        return Response(status=status.HTTP_200_OK)

    # POST /users/{user_id}/unsubscribe/
    @action(detail=True, methods=['POST'], url_path='unsubscribe')
    def unsubscribe(self, request, pk):
        return Response(status=status.HTTP_200_OK)

    # GET /users/subscribed/
    # list of writers
    @action(detail=False, methods=['GET'], url_path='subscribed')
    def list_of_subscribed(self):
        return Response(status=status.HTTP_200_OK)

    # GET /users/subscriber/
    # list of subscribers
    @action(detail=False, methods=['GET'], url_path='subscriber')
    def list_of_subscriber(self):
        return Response(status=status.HTTP_200_OK)
