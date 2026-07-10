from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'reviews'

router = DefaultRouter()
# router.register('', ReviewViewSet, basename='review')
urlpatterns = [
    path('', include(router.urls)),
]
