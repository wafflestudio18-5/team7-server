from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from posting.models import Posting
from posting.serializers import PostingSerializer, PostingRetrieveSerializer
from title.models import Title
from written.error_codes import *

# TODO use error code made by shchoi94
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
        posting = serializer.save()
        data_to_show = serializer.data
        data_to_show['title'] = titlename
        return Response(data_to_show, status=status.HTTP_201_CREATED)
        
    # GET /postings/{posting_id}/
    def retrieve(self, request, pk=None):
        posting = Posting.objects.get(pk=pk)
        if not posting:
            raise PostingDoesNotExistException()
        serializer = PostingRetrieveSerializer(posting)
        return Response(serializer.data)

    # PUT /postings/{posting_id}/
    def update(self, request, pk=None):
        user = request.user
        data = request.data
        if not data.writer == user:
            raise UserNotAuthorizedException()
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        posting = serializer.save()
        data_to_show = serializer.data
        data_to_show['title'] = titlename
        return Response(data_to_show)
    
    # DELETE /postings/{posting_id}/
    def delete(self, request, pk=None):
        if not request.user.is_superuser():
            raise UserNotAuthorizedException()
        posting = Posting.objects.get(pk=pk)
        if not posting:
            raise PostingDoesNotExistException()
        posting.delete()
        return Response(status=status.HTTP_200_OK)     
