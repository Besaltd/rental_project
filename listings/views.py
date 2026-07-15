from django.db.models import ProtectedError, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions as drf_permissions
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .filters import ListingFilter
from .models import Listing
from .permissions import IsLandlord, IsOwnerOrReadOnly
from .serializers import ListingSerializer, ListingWriteSerializer


class ListingViewSet(viewsets.ModelViewSet):

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filterset_class = ListingFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            return Listing.objects.filter(Q(is_active=True) | Q(owner=user))
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

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'detail': 'You cannot delete a listing that has existing reservations. Deactivate it instead of deleting it'},
                status=status.HTTP_400_BAD_REQUEST,
            )
