from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from title import Title
import datetime

class TitleViewSet(viewsets.GenericViewSet):
    queryset = Title.objects.all()

    # GET /titles/
    def list(self, request):
        time = request.query_param.get('time', None)
        order = request.query_param.get('order', None)
        is_official = request.query_param.get('official', False)
        query = request.query_param.get('name', None)
        titles = self.get_queryset()

        if time is not None:
            enddate = datetime.date.today()
            startdate = None
            if time is 'day':
                startdate = enddate - datetime.timedelta(days=1)
            elif time is 'week':
                startdate = enddate - datetime.timedelta(days=7)
            elif time is 'month':
                startdate = enddate - datetime.timedelta(days=31)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            titles = titles.filter(created_at__range=[, now])
        
        if is_official is True:
            titles = titles.filter(official=True)

        if query is not None:
            titles = titles.filter(name__contains=query)

        #TODO return serializer
        return Response()

    # GET /titles/{title_id}/
    def retrieve(self, request, pk=None):
        return Response()

    # POST /titles
    def create(self, request):
        return Response(status=status.HTTP_201_CREATED)

    # DELETE /titles/{title_id}/
    def delete(self, request, pk=None):
        return Response(status=status.HTTP_200_OK)