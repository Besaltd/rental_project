from rest_framework import permissions as drf_permissions
from rest_framework import viewsets

from .models import Review
from .permissions import IsReviewAuthorOrReadOnly
from .serializers import ReviewCreateSerializer, ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        queryset = Review.objects.select_related('listing', 'author')
        listing_id = self.request.query_params.get('listing')
        if listing_id:
            queryset = queryset.filter(listing_id=listing_id)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [drf_permissions.IsAuthenticated()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [drf_permissions.IsAuthenticated(), IsReviewAuthorOrReadOnly()]
        return [drf_permissions.AllowAny()]

    def perform_create(self, serializer):
        booking = serializer.validated_data['booking']
        serializer.save(author=self.request.user, listing=booking.listing)
