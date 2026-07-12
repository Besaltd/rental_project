from rest_framework import permissions as drf_permissions
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Listing
from .permissions import IsLandlord, IsOwnerOrReadOnly
from .serializers import ListingSerializer, ListingWriteSerializer


class ListingViewSet(viewsets.ModelViewSet):

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Listing.active.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ListingWriteSerializer
        return ListingSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [drf_permissions.IsAuthenticated(), IsLandlord()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [drf_permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [drf_permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
