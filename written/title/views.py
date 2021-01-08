from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from title.models import Title
from title.serializers import TitleSerializer, TitleSmallSerializer
from posting.models import Posting
from posting.serializers import PostingRetrieveSerializer, PostingDictSerializer
from django.utils import timezone
from written.error_codes import *
from django.db import connection

# API Titles
# GET /titles/
# POST /titles/
# GET /titles/{title_id}/
# DELETE /titles/{title_id}/


# from shchoi94
def dict_fetch_all(cursor):
    # Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class TitleViewSet(viewsets.GenericViewSet):
    TITLES_PAGE_SIZE_DEFAULT = 4
    POSTINGS_PAGE_SIZE_DEFAULT = 4
    queryset = Title.objects.all()
    permission_classes = (IsAuthenticated(), )
    serializer_class = TitleSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(), )
        return self.permission_classes
        
    def get_serializer_class(self):
        return self.serializer_class

    # GET /titles/
    def list(self, request):
        # query with time, official, name, order
        time = request.query_params.get('time', 'all')
        only_official = request.query_params.get('only_official', False)
        query = request.query_params.get('query', '')
        order = request.query_params.get('order', 'recent')
        
        if only_official:
            if only_official.lower() == 'true':
                only_official = True
            else:
                raise TitleDoesNotExistException()

        date_now = timezone.now()
        startdate = date_now
        enddate = date_now
        if time != 'all':
            if time not in ['day', 'week', 'month']:
                raise TitleDoesNotExistException()
                
            if time == 'day':
                startdate = enddate - timezone.timedelta(days=1)
            elif time == 'week':
                startdate = enddate - timezone.timedelta(weeks=1)
            elif time == 'month':
                startdate = enddate - timezone.timedelta(days=30)
            else:
                raise TitleDoesNotExistException()
            
        
        # concatenate MySQL statements and params for SQL statements
        try:
            my_cursor = int(request.GET['cursor'])
        except KeyError:
            if Title.objects.exists():
                my_cursor = Title.objects.last().id + 1
            else:
                my_cursor = 0
        try:
            page_size = int(request.GET['page_size'])
        except KeyError:
            page_size = self.TITLES_PAGE_SIZE_DEFAULT

        raw_query = '''
            SELECT * 
            FROM title_title
            WHERE id < %s
        '''
        params = [my_cursor]

        # time
        if time != 'all':
            raw_query += ' AND created_at >= %s AND created_at <= %s'
            params.append(startdate)
            params.append(enddate)

        # official
        if only_official:
            raw_query += ' AND is_official = %s'
            params.append(only_official)
        
        # name
        # this query should be improved
        # I've heard LIKE is inefficient but haven't found good alternatives
        if query != '':
            raw_query += ' AND name LIKE %s'
            query = '%' + query + '%'
            params.append(query)
        
        # order
        if order == 'recent':
            raw_query += ' ORDER BY created_at DESC'
        elif order == 'oldest':
            raw_query += ' ORDER BY created_at ASC'
        else:
            raise TitleDoesNotExistException()

        params.append(page_size+1)
        raw_query += ' LIMIT %s'

        with connection.cursor() as cursor:
            cursor.execute(raw_query, params)
            titles = dict_fetch_all(cursor)
        
        # SET RETURN VALUE: 'has_next'
        if len(titles) == page_size+1:
            has_next = True
            del titles[-1]
        else:
            has_next = False

        # SET RETURN VALUE: 'cursor'
        if has_next:
            next_cursor = titles[-1]['id']
        else:
            next_cursor = None

        titles_data = TitleSmallSerializer(titles, many=True).data
        return_data = {'titles': titles_data, 'has_next': has_next, 'cursor': next_cursor}
        return Response(return_data)

    # POST /titles/
    def create(self, request):
        data = request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET /titles/today/
    @action(detail=False, methods=['GET'], url_path='today')
    def today(self, request):
        try:
            title = Title.objects.get(pk=19)
        except:
            raise TitleDoesNotExistException()
        return Response(self.get_serializer(title).data)

    # GET /titles/{title_id}/postings/
    @action(detail=True, methods=['GET'], url_path='postings')
    def postings(self, request, pk=None):
        try:
            title = Title.objects.get(pk=pk)
        except Title.DoesNotExist:
           raise TitleDoesNotExistException()

        try:
            my_cursor = int(request.GET['cursor'])
        except KeyError:
            if Posting.objects.filter(title=title.id).exists():
                my_cursor = Posting.objects.last().id + 1
            else:
                my_cursor = 0
        try:
            page_size = int(request.GET['page_size'])
        except KeyError:
            page_size = self.POSTINGS_PAGE_SIZE_DEFAULT

        # my_cursor = int(request.query_params.get('cursor')) if request.query_params.get(
        #     'cursor') else Posting.objects.last().id + 1
        # page_size = int(request.query_params.get('page_size')) if request.query_params.get(
        #     'page_size') else self.POSTINGS_PAGE_SIZE_DEFAULT

        raw_query = f'''
            SELECT * 
            FROM posting_posting AS posting_table
            WHERE id < {my_cursor}
            AND title_id={title.id}
            AND is_public=1
            ORDER BY id DESC
            LIMIT {page_size + 1};
        '''
        with connection.cursor() as cursor:
            cursor.execute(raw_query)
            postings = dict_fetch_all(cursor)

        # SET RETURN VALUE: 'has_next'
        if len(postings) == page_size+1:
            has_next = True
            del postings[-1]
        else:
            has_next = False

        # SET RETURN VALUE: 'cursor'
        if has_next:
            next_cursor = postings[-1]['id']
        else:
            next_cursor = None
                        
        postings_data = PostingDictSerializer(postings, many=True).data

        return_data = {'postings': postings_data, 'has_next': has_next, 'cursor': next_cursor}
        return Response(return_data)

        