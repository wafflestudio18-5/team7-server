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
from subscription.models import Subscription
from written.error_codes import *
from user.token import check_token

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


def get_writer(writer_id):
    try:
        return User.objects.get(pk=writer_id)
    except User.DoesNotExist:
        return None


def get_subscription(subscriber_id, writer_id):
    try:
        return Subscription.objects.get(subscriber_id=subscriber_id, writer_id=writer_id)
    except Subscription.DoesNotExist:
        return None


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

    def check_nickname(self, data):
        nickname = data.get("nickname")
        if not nickname:
            return False
        if UserProfile.objects.filter(nickname=nickname).count() != 0:
            return False
        return True

    # POST /users/
    def create(self, request):
        if not check_token(request.data):
            raise InvalidFacebookTokenException
        if not self.check_nickname(request.data):
            raise NicknameDuplicateException
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:
            raise UserAlreadySignedUpException

        login(request, user)
        nickname = request.data.get('nickname')
        UserProfile.objects.create(user=user, nickname=nickname, facebook_id=request.data.get('facebookid'))
        data = {'user': serializer.data, 'access_token': user.auth_token.key}

        return Response(data, status=status.HTTP_201_CREATED)

    # PUT /users/login/
    @action(detail=False, methods=['PUT'])
    def login(self, request):
        if not check_token(request.data):
            raise InvalidFacebookTokenException
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
            raise UserNotAuthorizedException
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
                raise NicknameDuplicateException
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
        subscriber_id = request.user.id
        writer = get_writer(pk)
        if writer is None:
            raise UserDoesNotExistException()
        sb = get_subscription(subscriber_id, pk)
        if sb is None:
            Subscription.objects.create(subscriber_id=subscriber_id, writer_id=pk, is_active=False)
        if sb.is_active:  # if True -> error
            raise AlreadySubscribedException()
        sb.is_active = True
        sb.save()
        return Response(status=status.HTTP_200_OK)

    # POST /users/{user_id}/unsubscribe/
    @action(detail=True, methods=['POST'], url_path='unsubscribe')
    def unsubscribe(self, request, pk):
        subscriber_id = request.user.id
        writer = get_writer(pk)
        if writer is None:
            raise UserDoesNotExistException()
        sb = get_subscription(subscriber_id, pk)
        if sb is None or sb.is_active is False:  # if False or None -> error
            raise AlreadyUnsubscribedException()
        sb.is_active = False
        sb.save()
        return Response(status=status.HTTP_200_OK)

    # GET /users/subscribed/
    # list of writers
    @action(detail=False, methods=['GET'], url_path='subscribed')
    def list_of_subscribed(self,request):
        subscriber_id = request.user.id
        writers = Subscription.objects.raw('''SELECT updated_at FROM subscription_subscription WHERE subscriber_id = ORDER BY id DESC LIMIT 10''')
        result = []

        return Response(status=status.HTTP_200_OK)

    # GET /users/subscriber/
    # list of subscribers
    @action(detail=False, methods=['GET'], url_path='subscriber')
    def list_of_subscriber(self):
        return Response(status=status.HTTP_200_OK)
