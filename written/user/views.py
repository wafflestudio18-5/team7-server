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
from posting.models import Posting
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
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        if self.action in ('create', 'login'):
            return (AllowAny(),)
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
        try:
            user = User.objects.get(username=request.data.get("username"))
        except User.DoesNotExist:
            raise UserNotSignedUpException()
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        data = {'user': self.get_serializer(user).data, 'access_token': token.key}
        return Response(data, status=status.HTTP_200_OK)

    # PUT /users/logout/
    @action(detail=False, methods=['POST'])
    def logout(self, request):
        logout(request)
        return Response()

    # GET /users/me/  GET /users/{user_id}/
    def retrieve(self, request, pk=None):
        try:
            if pk == "me":
                user = request.user
            else:
                user = User.objects.get(id=pk)
        except User.DoseNotExist:
            raise UserDoesNotExistException()
        data = self.get_serializer(user).data
        data["count_public_postings"] = user.postings.filter(is_public=True).count()
        if pk == "me":
            data["count_all_postings"] = user.postings.count()
        else:
            try:
                Subscription.objects.get(subscriber=request.user, writer=user)
                subscribing = True
            except Subscription.DoesNotExist:
                subscribing = False
            data["subscribing"] = subscribing
        return Response(data, status=status.HTTP_200_OK)

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
                raise NicknameDuplicateException
            profile.nickname = nickname
            profile.save()
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    # GET /users/{user_id}/postings/
    @action(detail=True, methods=['GET'], url_path='postings')
    def postings_of_user(self, request, pk):
        try:
            user = User.objects.get(id=pk)
        except User.DoseNotExist:
            raise UserDoesNotExistException()

        try:
            cursor = int(request.GET['cursor'])
        except KeyError:
            cursor = 0
        try:
            page_size = int(request.GET['page_size'])
        except KeyError:
            page_size = 10

        pagination_query = f'SELECT posting.id AS id, user.id AS user_id, nickname, content, alignment, name, is_public, posting.created_at AS created_at ' \
                           f'FROM posting_posting AS posting ' \
                           f'INNER JOIN auth_user AS user ' \
                           f'INNER JOIN title_title AS title ' \
                           f'INNER JOIN user_userprofile AS profile ' \
                           f'ON posting.writer_id = user.id AND user.id = profile.user_id AND posting.title_id = title.id ' \
                           f'WHERE user.id = {user.id} AND posting.id > {cursor} AND posting.is_public = True ' \
                           f'ORDER BY posting.id ASC ' \
                           f'LIMIT {page_size + 1};'

        with connection.cursor() as cursor:
            cursor.execute(pagination_query)
            rows = dict_fetch_all(cursor)
        postings = []
        for i in range(min(len(rows), page_size)):
            row = rows[i]
            writer = {"id": row['user_id'], "nickname": row['nickname']}
            postings.append({"id": row["id"], "title": row["name"], "writer": writer,
                             "content": row["content"], "alignment": row["alignment"],
                             "id_public": row["is_public"], "created_at": row["created_at"]})
        if len(rows) == page_size + 1:
            next_cursor = rows[len(rows) - 2]['id']
            has_next = True
        else:
            next_cursor = None
            has_next = False

        return Response({"postings": postings, "has_next": has_next, "cursor": next_cursor}, status=status.HTTP_200_OK)

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
            sb = Subscription.objects.create(subscriber_id=subscriber_id, writer_id=pk, is_active=False)
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
        try:
            DEFAULT_CURSOR = Subscription.objects.last().id + 1
        except AttributeError:
            DEFAULT_CURSOR = 0
        DEFAULT_PAGE_SIZE = 10

        user_id = request.user.id
        my_cursor = int(request.query_params.get('cursor')) if request.query_params.get(
            'cursor') else DEFAULT_CURSOR
        page_size = int(request.query_params.get('page_size')) if request.query_params.get(
            'page_size') else DEFAULT_PAGE_SIZE

        # PAGINATION QUERY
        pagination_query = f'''
            SELECT user.id, userprofile.nickname, userprofile.description, subscription.id as 'subscription_id'
            FROM auth_user AS user
            INNER JOIN subscription_subscription subscription on {user_id} = subscription.subscriber_id
            INNER JOIN user_userprofile userprofile on user.id = userprofile.user_id
            WHERE subscription.id < {my_cursor} AND subscription.writer_id = user.id
            ORDER BY subscription.id DESC
            LIMIT {page_size + 1};
            '''
        with connection.cursor() as cursor:
            cursor.execute(pagination_query)
            rows = dict_fetch_all(cursor)

        # SET RETURN VALUE: 'has_next'
        if len(rows) == page_size + 1:
            has_next = True
            del rows[-1]
        else:
            has_next = False

        # SET RETURN VALUE: 'cursor'
        if has_next:
            next_cursor = rows[-1]['subscription_id']
        else:
            next_cursor = None

        for i in range(len(rows)):
            del rows[i]['subscription_id']

        data = {'writers': rows, 'has_next': has_next, 'cursor': next_cursor}
        return Response(data, status=status.HTTP_200_OK)

    # GET /users/subscriber/
    # list of subscribers
    @action(detail=False, methods=['GET'], url_path='subscriber')
    def list_of_subscriber(self, request):
        try:
            DEFAULT_CURSOR = Subscription.objects.last().id + 1
        except AttributeError:
            DEFAULT_CURSOR = 0
        DEFAULT_PAGE_SIZE = 10

        user_id = request.user.id
        my_cursor = int(request.query_params.get('cursor')) if request.query_params.get(
            'cursor') else DEFAULT_CURSOR
        page_size = int(request.query_params.get('page_size')) if request.query_params.get(
            'page_size') else DEFAULT_PAGE_SIZE

        # PAGINATION QUERY
        pagination_query = f'''
                    SELECT user.id, userprofile.nickname, userprofile.description, subscription.id as 'subscription_id'
                    FROM auth_user AS user
                    INNER JOIN subscription_subscription subscription on {user_id} = subscription.writer_id
                    INNER JOIN user_userprofile userprofile on user.id = userprofile.user_id
                    WHERE subscription.id < {my_cursor} AND subscription.subscriber_id = user.id
                    ORDER BY subscription.id DESC
                    LIMIT {page_size + 1};
                    '''
        with connection.cursor() as cursor:
            cursor.execute(pagination_query)
            rows = dict_fetch_all(cursor)

        # SET RETURN VALUE: 'has_next'
        if len(rows) == page_size + 1:
            has_next = True
            del rows[-1]
        else:
            has_next = False

        # SET RETURN VALUE: 'cursor'
        if has_next:
            next_cursor = rows[-1]['subscription_id']
        else:
            next_cursor = None

        for i in range(len(rows)):
            del rows[i]['subscription_id']

        data = {'subscribers': rows, 'has_next': has_next, 'cursor': next_cursor}
        return Response(data, status=status.HTTP_200_OK)
