from django.urls import include, path
from rest_framework.routers import SimpleRouter
from posting.views import PostingViewSet

app_name = 'posting'

router = SimpleRouter()
router.register('posting', PostingViewSet, basename='posting')  # /api/v1/posting/

urlpatterns = [
    path('', include((router.urls))),
]
