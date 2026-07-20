from django.db.models import ProtectedError, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from rest_framework import permissions as drf_permissions
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .filters import ListingFilter
from .models import Listing
from .permissions import IsLandlord, IsOwnerOrReadOnly
from .serializers import ListingSerializer, ListingWriteSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Listings'],
        summary='Search listings',
        description=(
            'Public. Only active listings are returned, except that an '
            'authenticated landlord also sees their own inactive ones. '
            'Combine price/rooms/city/property_type filters, ?search= '
            'for keywords in title/description, and ?ordering= for sorting.'
        ),
    ),
    create=extend_schema(
        tags=['Listings'],
        summary='Create a listing',
        description='Landlord role required. owner is set from the current user.',
        examples=[
            OpenApiExample(
                'Cozy apartment in Berlin',
                value={
                    'title': 'Cozy studio near Alexanderplatz',
                    'description': 'Bright, quiet studio, 5 min walk to the U-Bahn.',
                    'city': 'Berlin',
                    'address': 'Alexanderplatz 1',
                    'price': '1650.00',
                    'rooms': 1,
                    'property_type': 'apartment',
                },
                request_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        tags=['Listings'],
        summary='Edit a listing',
        description=(
            'Owner only. Also used to toggle is_active — the API is the '
            'only way to reactivate a listing once deactivated.'
        ),
    ),
    destroy=extend_schema(
        tags=['Listings'],
        summary='Delete a listing',
        description=(
            'Owner only. Fails with 400 if the listing has any bookings — '
            'deactivate it instead (see PATCH is_active) rather than deleting.'
        ),
    ),
    retrieve=extend_schema(
        tags=['Listings'], summary='Listing detail', description='Public.'),
)
class ListingViewSet(viewsets.ModelViewSet):

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
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
