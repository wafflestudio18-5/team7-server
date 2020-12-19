from django.urls import include, path
from rest_framework.routers import SimpleRouter
from posting.views import PostingViewSet

app_name = 'posting'

router = SimpleRouter()
router.register('postings', PostingViewSet, basename='postings')  # /postings/

urlpatterns = [
    path('', include((router.urls))),
]
