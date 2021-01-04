from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from title.models import Title
from title.serializers import TitleSerializer, TitleUpdateSerializer
from django.utils import timezone
from written.error_codes import *

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

class TitleViewSet(viewsets.GenericViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    
    def get_serializer_class(self):
        return self.serializer_class

    # GET /titles/
    def list(self, request):
        # my_cursor = int(request.query_params.get('cursor')) if request.query_params.get(
        #     'cursor') else Title.objects.last().id + 1
        # page_size = int(request.query_params.get('page_size')) if request.query_params.get(
        #     'page_size') else 10

        # user = request.user

        time = request.query_params.get('time', 'all')
        order = request.query_params.get('order', 'recent')
        official = request.query_params.get('official', 'true')
        query = request.query_params.get('query', '')

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
        elif official.lower() == 'false':
            official = False
        else:
            raise TitleDoesNotExistException()

        params = []
        raw_query = '''
            SELECT * 
            FROM title_title
        '''
        if time != 'all':
            raw_query += 'WHERE created_at >= %s AND created_at <= %s'
            params.append(startdate)
            params.append(enddate)
            raw_query += 'AND is_official = %s'
        else:
            raw_query += 'WHERE is_official = %s'
        
        params.append(official)
        
        # name query should be improved
        # I heard LIKE is inefficient
        # but haven't found good alternatives
        if query != '':
            raw_query += ' AND name LIKE %s'
            query = '%' + query + '%'
            params.append(query)
        
        if order == 'recent':
            raw_query += ' ORDER BY created_at DESC'
        elif order == 'oldest':
            raw_query += ' ORDER BY created_at ASC'
        else:
            raise TitleDoesNotExistException()
        
        # for debugging
        # print(raw_query)
        # print(params)

        titles = Title.objects.raw(raw_query=raw_query, params=params)

        return Response(self.get_serializer(titles, many=True).data)

    # POST /titles/
    def create(self, request):
        data = request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET /titles/{title_id}/
    def retrieve(self, request, pk=None):
        title = get_title(pk)
        if not title:
            raise TitleDoesNotExistException()
        return Response(self.get_serializer(title).data)
