from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action


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

class UserViewSet(viewsets.GenericViewSet):
    # API User===============================================================
    # =======================================================================
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
        return Response(status=status.HTTP_200_OK)

    # POST /users/{user_id}/unsubscribe/
    @action(detail=True, methods=['POST'], url_path='unsubscribe')
    def unsubscribe(self, request, pk):
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
