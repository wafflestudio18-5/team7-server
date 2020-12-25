from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from posting.models import Posting
from title.models import Title

class PostingViewSet(viewsets.GenericViewSet):
    queryset = Posting.objects.all()
    # TODO serializer_class = PostingSerializer
    # TODO permission_classes = (IsAuthenticated, )

    # TODO get_permissions(self):
    # TODO get_serializer_class(self):

    def list(self, request):
        return Response(status=status.HTTP_200_OK)
    
    # POST /postings/
    def create(self, request):
        return Response()
        
    # GET /postings/{posting_id}/
    def retrieve(self, request, pk=None):
        return Response()

    # PUT /postings/{posting_id}/
    def update(self, request, pk=None):
        return Response()
