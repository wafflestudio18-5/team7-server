from django.urls import include, path
from rest_framework.routers import SimpleRouter
from title.views import TitleViewSet

app_name = 'title'

router = SimpleRouter()
router.register('titles', TitleViewSet, basename='titles')  # /titles/

urlpatterns = [
    path('', include((router.urls))),
]
