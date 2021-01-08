from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from posting.models import Posting
from posting.serializers import PostingSerializer, PostingRetrieveSerializer, PostingUpdateSerializer
from scrap.models import Scrap
from subscription.models import Subscription
from title.models import Title
from written.error_codes import *
from django.utils import timezone


from django.db import connection


def dict_fetch_all(cursor):
    # Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def get_posting(posting_id):
    try:
        return Posting.objects.get(pk=posting_id)
    except Posting.DoesNotExist:
        return None


class PostingViewSet(viewsets.GenericViewSet):
    queryset = Posting.objects.all()
    serializer_class = PostingSerializer
    permission_classes = (IsAuthenticated(), )

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(), )
        return self.permission_classes

    def get_serializer_class(self):
        return self.serializer_class

    def list(self, request):
        return Response(status=status.HTTP_200_OK)

    # POST /postings/
    def create(self, request):
        user = request.user
        data = request.data
        titlename = data.get('title')
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        posting = serializer.save(writer=user)
        data_to_show = serializer.data
        data_to_show['title'] = titlename

        if not user.userprofile.first_posted_at:
            user.userprofile.first_posted_at = timezone.now()
        
        return Response(data_to_show, status=status.HTTP_201_CREATED)

    # GET /postings/{posting_id}/
    def retrieve(self, request, pk=None):
        posting = get_posting(pk)
        if not posting:
            raise PostingDoesNotExistException()
        serializer = PostingRetrieveSerializer(posting)
        return Response(serializer.data)

    # PUT /postings/{posting_id}/
    def update(self, request, pk=None):
        user = request.user
        data = request.data

        try:
            posting = get_posting(pk)
        except Posting.DoesNotExist:
            raise PostingDoesNotExistException()

        if data.get['is_public'] is not None and not bool(data.get['is_public']) and posting.is_public:
            make_private = True
        else:
            make_private = False

        if posting.writer != user:
            raise UserNotAuthorizedException()

        serializer = PostingUpdateSerializer(posting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(posting, serializer.validated_data)

        if make_private:
            Scrap.objects.filter(posting_id=posting.id).delete()

        data_to_show = serializer.data
        data_to_show['title'] = posting.title.name
        return Response(data_to_show)

    # DELETE /postings/{posting_id}/
    def delete(self, request, pk=None):
        posting = get_posting(pk)
        if not posting:
            raise PostingDoesNotExistException()
        if request.user != posting.writer:
            raise UserNotAuthorizedException()
        posting.delete()
        return Response(status=status.HTTP_200_OK)

    # ==API Scrap===============================================================================
    # POST postings/{posting_id}/scrap/
    # POST postings/{posting_id}/unscrap/
    # GET postings/scrapped/
    # ==API Subscription========================================================================
    # GET postings/subscribed/
    # ==========================================================================================
    # POST postings/{posting_id}/scrap
    @action(detail=True, methods=['POST'], url_path='scrap')
    def scrap(self, request, pk):
        user_id = request.user.id
        try:
            posting = Posting.objects.get(pk=pk)
        except Posting.DoesNotExist:
            raise PostingDoesNotExistException()
        if not posting.is_public:
            raise PostingDoesNotExistException()
        try:
            Scrap.objects.get(user_id=user_id, posting_id=posting.id)
            raise AlreadyScrappedException()
        except Scrap.DoesNotExist:
            Scrap.objects.create(user_id=user_id, posting_id=posting.id)
        return Response(status=status.HTTP_200_OK)

    # POST postings/{posting_id}/unscrap
    @action(detail=True, methods=['POST'], url_path='unscrap')
    def unscrap(self, request, pk):
        user_id = request.user.id
        try:
            posting = Posting.objects.get(pk=pk)
        except Posting.DoesNotExist:
            raise PostingDoesNotExistException()
        try:
            scrap = Scrap.objects.get(user_id=user_id, posting_id=posting.id)
            scrap.delete()
        except Scrap.DoesNotExist:
            raise AlreadyUnscrappedException()
        return Response(status=status.HTTP_200_OK)

    # GET postings/scrapped/
    @action(detail=False, methods=['GET'], url_path='scrapped')
    def scrapped(self, request):
        try:
            DEFAULT_CURSOR = Scrap.objects.last().id + 1
        except AttributeError:
            DEFAULT_CURSOR = 0
        DEFAULT_PAGE_SIZE = 5

        user_id = request.user.id
        my_cursor = int(request.query_params.get('cursor')) if request.query_params.get(
            'cursor') else DEFAULT_CURSOR
        page_size = int(request.query_params.get('page_size')) if request.query_params.get(
            'page_size') else DEFAULT_PAGE_SIZE

        # PAGINATION QUERY
        pagination_query = f'''
                    SELECT posting.id, posting.writer_id as 'writer', title.name as 'title',posting.content, 
                    posting.alignment, posting.created_at, posting.is_public, scrap.id as 'scrap_id', userprofile.nickname as 'nickname'
                    FROM  posting_posting AS posting
                    INNER JOIN user_userprofile userprofile on posting.writer_id = userprofile.user_id
                    INNER JOIN title_title title on posting.title_id = title.id
                    INNER JOIN scrap_scrap scrap on posting.id = scrap.posting_id
                    WHERE scrap.id < {my_cursor} AND scrap.user_id = {user_id}
                    ORDER BY scrap.id DESC
                    LIMIT {page_size + 1};
                    '''
        with connection.cursor() as cursor:
            cursor.execute(pagination_query)
            rows = dict_fetch_all(cursor)

        # set 'has_next', delete surplus row
        if len(rows) == page_size + 1:
            has_next = True
            del rows[-1]
        else:
            has_next = False

        # set 'cursor', delete field 'scrap_id'
        if has_next:
            next_cursor = rows[-1]['scrap_id']
        else:
            next_cursor = None
        for i in range(len(rows)):
            rows[i]['writer'] = {'id': rows[i]['writer'], 'nickname': rows[i]['nickname']}
            del rows[i]['scrap_id']
            del rows[i]['nickname']

        data = {'stored_postings': rows, 'has_next': has_next, 'cursor': next_cursor}
        return Response(data, status=status.HTTP_200_OK)

    # GET postings/subscribed/
    @action(detail=False, methods=['GET'], url_path='subscribed')
    def subscribed(self, request):
        try:
            DEFAULT_CURSOR = Posting.objects.last().id + 1
        except AttributeError:
            DEFAULT_CURSOR = 0
        DEFAULT_PAGE_SIZE = 5

        user_id = request.user.id
        my_cursor = int(request.query_params.get('cursor')) if request.query_params.get(
            'cursor') else DEFAULT_CURSOR
        page_size = int(request.query_params.get('page_size')) if request.query_params.get(
            'page_size') else DEFAULT_PAGE_SIZE

        # PAGINATION QUERY
        pagination_query = f'''
                        SELECT posting.id, posting.writer_id as 'writer', title.name as 'title',posting.content, 
                        posting.alignment, posting.created_at, posting.is_public, userprofile.nickname as 'nickname'
                        FROM  posting_posting AS posting
                        INNER JOIN subscription_subscription subscription on subscription.subscriber_id = {user_id} and subscription.writer_id = posting.writer_id
                        INNER JOIN user_userprofile userprofile on posting.writer_id = userprofile.user_id
                        INNER JOIN title_title title on posting.title_id = title.id
                        WHERE posting.id < {my_cursor} 
                        ORDER BY posting.id DESC
                        LIMIT {page_size + 1};
                        '''
        with connection.cursor() as cursor:
            cursor.execute(pagination_query)
            rows = dict_fetch_all(cursor)

        # set 'has_next', delete surplus row
        if len(rows) == page_size + 1:
            has_next = True
            del rows[-1]
        else:
            has_next = False

        # set 'cursor', delete field 'scrap_id'
        if has_next:
            next_cursor = rows[-1]['id']
        else:
            next_cursor = None
        for i in range(len(rows)):
            rows[i]['writer'] = {'id': rows[i]['writer'], 'nickname': rows[i]['nickname']}
            del rows[i]['nickname']

        data = {'stored_postings': rows, 'has_next': has_next, 'cursor': next_cursor}
        return Response(data, status=status.HTTP_200_OK)

