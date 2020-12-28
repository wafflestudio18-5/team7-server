from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from title.models import Title
from title.serializers import TitleSerializer
import datetime

# API Titles
# GET /titles/
# POST /titles/
# GET /titles/{title_id}/
# DELETE /titles/{title_id}/


class TitleViewSet(viewsets.GenericViewSet):
    queryset = Title.objects.all()

    # GET /titles/
    def list(self, request):
        time = request.query_param.get('time', None)
        order = request.query_param.get('order', None)
        is_official = request.query_param.get('official', None)
        query = request.query_param.get('name', None)
        titles = self.get_queryset()

        if time is not None:
            if time is not in ['day', 'week', 'month']:
                raise TitleDoesNotExistException()
                
            date_today = datetime.now()
            month_first_day = date_today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            print(month_first_day)

            if time is 'day':
                startdate = datetime.date.today()
            elif time is 'week':
                startdate = enddate - datetime.timedelta(days=7)
            elif time is 'month':
                startdate = enddate - datetime.timedelta(days=31)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            titles = titles.filter(created_at__range=[startdate, enddate])
        
            
        if is_official.upper() is 'TRUE':
            titles = titles.filter(official=True)

        if query is not None:
            titles = titles.filter(name__contains=query)
        
        if order is not None:
            titles = titles.order_by('created_at')

        titles = titles.objects.raw(
            'SELECT * FROM title WHERE EXTRACT(\'year\') FROM '
            ) #TODO

        return Response(self.get_serializer(titles, many=True).data)

    # POST /titles/
    def create(self, request):
        if not request.user.is_superuser():
            raise UserNotAuthorizedException()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET /titles/{title_id}/
    def retrieve(self, request, pk=None):
        if queryset.filter(pk=pk).exists():
            raise TitleDoesNotExistException()
        title = self.get_object()
        return Response(self.get_serializer(title))

    # DELETE /titles/{title_id}/
    def delete(self, request, pk=None):
        if not request.user.is_superuser():
            raise UserNotAuthorizedException()
        title = self.get_object()
        title.delete()
        return Response(status=status.HTTP_200_OK)