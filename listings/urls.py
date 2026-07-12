from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ListingViewSet

app_name = 'listings'

router = DefaultRouter()
router.register('', ListingViewSet, basename='listing')

urlpatterns = [
    path('', include(router.urls)),
]
