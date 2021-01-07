from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from posting.models import Posting
from posting.serializers import PostingSerializer, PostingRetrieveSerializer, PostingUpdateSerializer
from subscription.models import Subscription
from title.models import Title
from written.error_codes import *
from django.utils import timezone


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
        
        if posting.writer != user:
            raise UserNotAuthorizedException()
        
        was_public = posting.is_public
        serializer = PostingUpdateSerializer(posting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(posting, serializer.validated_data)
        if was_public and serializer.validated_data['is_public'] == False:
            Subscription.objects.filter()
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

    
