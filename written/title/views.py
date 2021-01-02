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
        time = request.query_params.get('time', 'all')
        order = request.query_params.get('order', 'recent')
        official = request.query_params.get('official', 'false')
        query = request.query_params.get('query', None)
        titles = self.get_queryset()

        if time != 'all':
            if time not in ['day', 'week', 'month']:
                raise TitleDoesNotExistException()
                
            date_now = timezone.now()
            startdate = date_now
            enddate = date_now
            if time == 'day':
                startdate = enddate - timezone.timedelta(days=1)
            elif time == 'week':
                startdate = enddate - timezone.timedelta(weeks=1)
            elif time == 'month':
                startdate = enddate - timezone.timedelta(days=30)
            else:
                raise TitleDoesNotExistException()
            titles = titles.filter(created_at__range=[startdate, enddate])
        
            
        if official.lower() == 'true':
            titles = titles.filter(is_official=True)

        if query is not None:
            titles = titles.filter(name__contains=query)
        
        if order == 'recent':
            titles = titles.order_by('-created_at')
        elif order == 'oldest':
            titles = titles.order_by('created_at')
        else:
            raise TitleDoesNotExistException()

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

    # deprecated
    # # PUT /titles/{title_id}/
    # def update(self, request, pk=None):
    #     title = get_title(pk)
    #     if not request.user.is_superuser:
    #         raise UserNotAuthorizedException()
    #     if not title:
    #         raise TitleDoesNotExistException()
    #     serializer = TitleUpdateSerializer(title, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.update(title, serializer.validated_data)
    #     return Response(self.get_serializer(title).data)

    # # DELETE /titles/{title_id}/
    # def delete(self, request, pk=None):
    #     if not request.user.is_superuser:
    #         raise UserNotAuthorizedException()
    #     title = get_title(pk)
    #     if not title:
    #         raise TitleDoesNotExistException()
    #     title.delete()
    #     return Response()
