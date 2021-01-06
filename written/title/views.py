from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from title.models import Title
from title.serializers import TitleSerializer, TitleUpdateSerializer
from posting.models import Posting
from posting.serializers import PostingRetrieveSerializer
from django.utils import timezone
from written.error_codes import *
from django.db import connection

# API Titles
# GET /titles/
# POST /titles/
# GET /titles/{title_id}/
# DELETE /titles/{title_id}/

def get_title(title_id):
    try:
        return Title.objects.get(pk=title_id)
    except Title.DoesNotExist:
        return None

# from shchoi94
def dict_fetch_all(cursor):
    # Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class TitleViewSet(viewsets.GenericViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    
    def get_serializer_class(self):
        return self.serializer_class

    # GET /titles/
    def list(self, request):
        # query with time, official, name, order
        time = request.query_params.get('time', 'all')
        official = request.query_params.get('official', 'all')
        query = request.query_params.get('query', '')
        order = request.query_params.get('order', 'recent')

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
            
        if official.lower() == 'true':
            official = True
        elif official.lower() == 'all':
            official = False
        else:
            raise TitleDoesNotExistException()
        
        # concatenate MySQL statements and params for SQL statements
        my_cursor = int(request.query_params.get('cursor')) if request.query_params.get(
            'cursor') else Title.objects.last().id + 1
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
        if official:
            raw_query += ' AND is_official = %s'
            params.append(official)
        
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

        page_size = int(request.query_params.get('page_size')) if request.query_params.get(
            'page_size') else 5

        params.append(page_size)
        raw_query += ' LIMIT %s'

        with connection.cursor() as cursor:
            cursor.execute(raw_query, params)
            titles = dict_fetch_all(cursor)
        titles_data = self.get_serializer(titles, many=True).data
        
        # SET RETURN VALUE: 'cursor'
        if len(titles) > 0:
            title_id = titles[-1]['id']
            result_cursor = Title.objects.get(pk=title_id).id
        else:
            result_cursor = my_cursor

        # SET RETURN VALUE: 'has_next'
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM title_title WHERE id < %s",
                           [result_cursor])
            next_rows = dict_fetch_all(cursor)
        if len(next_rows) > 0:
            has_next = True
        else:
            has_next = False

        return_data = {'titles': titles_data, 'has_next': has_next, 'cursor': result_cursor}
        return Response(titles_data)

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
            title = Title.objects.last()
        except:
            raise TitleDoesNotExistException()
        return Response(self.get_serializer(title).data)

    # GET /titles/{title_id}/postings/
    @action(detail=True, methods=['GET'], url_path='postings')
    def postings(self, request, pk=None):
        try:
            title = get_title(pk)
        except Title.DoesNotExist:
            raise TitleDoesNotExistException()
        
        my_cursor = int(request.query_params.get('cursor')) if request.query_params.get(
            'cursor') else Posting.objects.last().id + 1
        page_size = int(request.query_params.get('page_size')) if request.query_params.get(
            'page_size') else 2

        raw_query = '''
            SELECT * 
            FROM posting_posting AS posting_table
            WHERE id < %s
            AND title_id=%s
            LIMIT %s
        '''
        params = [my_cursor, title.id, page_size]

        with connection.cursor() as cursor:
            cursor.execute(raw_query, params)
            postings = dict_fetch_all(cursor)
        postings_data = postings

        # SET RETURN VALUE: 'cursor'
        if len(postings) > 0:
            posting_id = postings[-1]['id']
            result_cursor = Posting.objects.get(pk=posting_id).id
        else:
            result_cursor = my_cursor

        # SET RETURN VALUE: 'has_next'
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM title_title WHERE id < %s",
                           [result_cursor])
            next_rows = dict_fetch_all(cursor)
        if len(next_rows) > 0:
            has_next = True
        else:
            has_next = False

        return_data = {'postings': postings_data, 'has_next': has_next, 'cursor': result_cursor}

        return Response(return_data)

        