from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from posting.models import Posting
from posting.serializers import PostingSerializer, PostingRetrieveSerializer, PostingUpdateSerializer
from scrap.models import Scrap
from title.models import Title
from written.error_codes import *
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

    def get_serializer_class(self):
        return self.serializer_class

    # TODO? permission_classes = (IsAuthenticated, )
    # TODO? get_permissions(self):

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
        posting = get_posting(pk)

        if posting.writer != user:
            raise UserNotAuthorizedException()

        serializer = PostingUpdateSerializer(posting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(posting, serializer.validated_data)
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

    # API Scrap===============================================================================
    # POST postings/{posting_id}/scrap/
    # POST postings/{posting_id}/unscrap/
    # GET postings/scrapped/
    # =========================================================================================

    # POST postings/{posting_id}/scrap
    @action(detail=True, methods=['POST'], url_path='scrap')
    def scrap(self, request, pk):
        user_id = request.user.id
        try:
            posting = Posting.objects.get(pk=pk)
        except Posting.DoesNotExist:
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
        # INIT VARIABLES
        my_cursor = int(request.query_params.get('cursor')) if request.query_params.get(
            'cursor') else Scrap.objects.last().id + 1
        page_size = int(request.query_params.get('page_size'))
        user_id = request.user.id

        # PAGINATION QUERY
        my_query = '''
                    SELECT posting_table.id, posting_table.title_id as 'title',posting_table.content,scrap_table.created_at as 'scrapped_at'
                    FROM  posting_posting AS posting_table
                    JOIN (SELECT * FROM scrap_scrap WHERE id < %s AND user_id = %s) AS scrap_table
                    WHERE scrap_table.posting_id=posting_table.id
                    ORDER BY scrap_table.id DESC
                    LIMIT %s;
                    '''
        with connection.cursor() as cursor:
            cursor.execute(my_query, [my_cursor, user_id, page_size])
            rows = dict_fetch_all(cursor)

        # SET RETURN VALUE: 'cursor'
        if len(rows) > 0:
            posting_id = rows[-1]['id']
            result_cursor = Scrap.objects.get(posting_id=posting_id,user_id=user_id).id
        else:
            result_cursor = my_cursor

        # SET RETURN VALUE: 'has_next'
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM scrap_scrap WHERE id < %s AND user_id = %s",
                           [result_cursor, user_id])
            next_rows = dict_fetch_all(cursor)
        if len(next_rows) > 0:
            has_next = True
        else:
            has_next = False

        # title_id -> Title.name
        for i in range(len(rows)):
            rows[i]['title'] = Title.objects.get(pk=rows[i]['title']).name

        data = {'stored_postings': rows, 'has_next': has_next, 'cursor': result_cursor}
        return Response(data, status=status.HTTP_200_OK)
