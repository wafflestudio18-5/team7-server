from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from posting.models import Posting
from posting.serializers import PostingSerializer, PostingRetrieveSerializer, PostingUpdateSerializer
from title.models import Title
from written.error_codes import *

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
