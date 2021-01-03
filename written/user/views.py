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
from django.db import connection


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

def dict_fetch_all(cursor):
    # Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


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
            raise InvalidFacebookTokenException()
        if not self.check_nickname(request.data):
            raise NicknameDuplicateException()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:
            raise UserAlreadySignedUpException()

        login(request, user)
        nickname = request.data.get('nickname')
        UserProfile.objects.create(user=user, nickname=nickname, facebook_id=request.data.get('facebookid'))
        data = {'user': serializer.data, 'access_token': user.auth_token.key}

        return Response(data, status=status.HTTP_201_CREATED)

    # PUT /users/login/
    @action(detail=False, methods=['PUT'])
    def login(self, request):
        if not check_token(request.data):
            raise InvalidFacebookTokenException()
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
            raise UserNotAuthorizedException()
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
                raise NicknameDuplicateException()
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
    def list_of_subscribed(self, request):
        # INIT VARIABLES
        my_cursor = int(request.query_params.get('cursor')) if request.query_params.get(
            'cursor') else Subscription.objects.last().id + 1
        page_size = int(request.query_params.get('page_size'))
        user_id = request.user.id
        # user_id = 1

        # PAGINATION QUERY
        my_query = '''
            SELECT user_table.id, user_table.username,subs_table.id as 'cursor'
            FROM auth_user AS user_table
            JOIN (SELECT * FROM subscription_subscription WHERE id < %s AND subscriber_id = %s) AS subs_table
            WHERE writer_id=user_table.id
            ORDER BY subs_table.id DESC
            LIMIT %s;
            '''
        with connection.cursor() as cursor:
            cursor.execute(my_query, [my_cursor, user_id, page_size])
            rows = dict_fetch_all(cursor)

        # SET RETURN VALUE: 'cursor'
        if len(rows) > 0:
            result_cursor = rows[-1]['cursor']
        else:
            result_cursor = my_cursor

        # SET RETURN VALUE: 'has_next'
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM subscription_subscription WHERE id < %s AND subscriber_id = %s",
                                     [result_cursor, user_id])
            next_rows = dict_fetch_all(cursor)
        if len(next_rows) > 0:
            has_next = True
        else:
            has_next = False

        data = {'writers': rows, 'has_next': has_next, 'cursor': result_cursor}
        return Response(data, status=status.HTTP_200_OK)

    # GET /users/subscriber/
    # list of subscribers
    @action(detail=False, methods=['GET'], url_path='subscriber')
    def list_of_subscriber(self, request):
        # INIT VARIABLES
        my_cursor = int(request.query_params.get('cursor')) if request.query_params.get(
            'cursor') else Subscription.objects.last().id + 1
        page_size = int(request.query_params.get('page_size'))
        user_id = request.user.id
        # user_id = 1

        # PAGINATION QUERY
        my_query = '''
                    SELECT user_table.id, user_table.username,subs_table.id as 'cursor'
                    FROM auth_user AS user_table
                    JOIN (SELECT * FROM subscription_subscription WHERE id < %s AND writer_id = %s) AS subs_table
                    WHERE subscriber_id=user_table.id
                    ORDER BY subs_table.id DESC
                    LIMIT %s;
                    '''
        with connection.cursor() as cursor:
            cursor.execute(my_query, [my_cursor, user_id, page_size])
            rows = dict_fetch_all(cursor)

        # SET RETURN VALUE: 'cursor'
        if len(rows) > 0:
            result_cursor = rows[-1]['cursor']
        else:
            result_cursor = my_cursor

        # SET RETURN VALUE: 'has_next'
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM subscription_subscription WHERE id < %s AND writer_id = %s",
                           [result_cursor, user_id])
            next_rows = dict_fetch_all(cursor)
        if len(next_rows) > 0:
            has_next = True
        else:
            has_next = False

        data = {'subscribers': rows, 'has_next': has_next, 'cursor': result_cursor}
        return Response(data, status=status.HTTP_200_OK)
