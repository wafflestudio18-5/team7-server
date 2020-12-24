from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from subscription.models import Subscription
from written.error_codes import *


# API User==================================================================
# POST /users/
# PUT /users/login/
# GET /users/me/
# GET /users/{user_id}/
# PUT /users/me/
# GET /users/{user_id}/postings/

# API Subscription===========================================================
# POST /users/{user_id}/subscribe/
# POST /users/{user_id}/unsubscribe/
# GET /users/subscribed/
# GET /users/subscriber/

def get_writer(pk):
    try:
        return User.objects.get(pk=pk)
    except User.DoesNotExist:
        return None


def get_subscription(subscriber_id, writer_id, sub_or_unsub):
    try:
        return Subscription.objects.get(subscriber_id=1, writer_id=writer_id)
    except Subscription.DoesNotExist:
        if sub_or_unsub == "sub":
            return Subscription.objects.create(subscriber_id=1, writer_id=writer_id, is_active=False)
        else:
            return None


class UserViewSet(viewsets.GenericViewSet):
    # API User===============================================================
    # =======================================================================
    # POST /users/
    def create(self, request):
        return Response(status=status.HTTP_200_OK)

    # PUT /users/login/
    def login(self, request):
        return Response(status=status.HTTP_200_OK)

    def logout(self, request):
        return Response(status=status.HTTP_200_OK)

    # GET /users/me/
    @action(detail=False, methods=['GET'], url_path='me')
    def retrieve_me(self, request, pk):
        return Response(status=status.HTTP_200_OK)

    # GET /users/{user_id}/
    def retrieve(self, request, pk):
        return Response(status=status.HTTP_200_OK)

    # PUT /users/me/
    def update(self, request):
        return Response(status=status.HTTP_200_OK)

    # GET /users/{user_id}/postings/
    @action(detail=True, methods=['GET'], url_path='postings')
    def postings_of_user(self, request, pk):
        return Response(status=status.HTTP_200_OK)

    # API Subscription===========================================================
    # ===========================================================================
    # POST /users/{user_id}/subscribe/
    @action(detail=True, methods=['POST'], url_path='subscribe')
    def subscribe(self, request, pk):
        subscriber_id = request.user.id
        writer = get_writer(pk)
        if writer is None:
            return Response(error_10003, status=status.HTTP_400_BAD_REQUEST)
        sb = get_subscription(subscriber_id, pk, "sub")
        if sb.is_active:  # if True -> error
            return Response(error_30001, status=status.HTTP_400_BAD_REQUEST)
        sb.is_active = True
        sb.save()
        return Response(status=status.HTTP_200_OK)

    # POST /users/{user_id}/unsubscribe/
    @action(detail=True, methods=['POST'], url_path='unsubscribe')
    def unsubscribe(self, request, pk):
        subscriber_id = request.user.id
        writer = get_writer(pk)
        if writer is None:
            return Response(error_10003, status=status.HTTP_400_BAD_REQUEST)
        sb = get_subscription(subscriber_id, pk, "unsub")
        if sb.is_active is False or sb is None:  # if False or None -> error
            return Response(error_30002, status=status.HTTP_400_BAD_REQUEST)
        sb.is_active = False
        sb.save()
        return Response(status=status.HTTP_200_OK)

    # GET /users/subscribed/
    # list of writers
    @action(detail=False, methods=['GET'], url_path='subscribed')
    def list_of_subscribed(self):
        return Response(status=status.HTTP_200_OK)

    # GET /users/subscriber/
    # list of subscribers
    @action(detail=False, methods=['GET'], url_path='subscriber')
    def list_of_subscriber(self):
        return Response(status=status.HTTP_200_OK)
