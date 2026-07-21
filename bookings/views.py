from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from rest_framework import permissions as drf_permissions
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import BookingFilter
from .models import Booking
from .permissions import IsBookingTenantOrListingOwner, IsTenant
from .serializers import BookingCreateSerializer, BookingSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Bookings'],
        summary='List own bookings',
        description=(
            'A tenant sees their own bookings; a landlord sees bookings '
            'made on their listings. Use the status/date/is_completed '
            'query params to narrow the list down.'
        ),
    ),
    create=extend_schema(
        tags=['Bookings'],
        summary='Create a booking',
        description=(
            'Tenant role required. Cannot book your own listing, cannot '
            'start in the past, and dates must not overlap an existing '
            'pending/confirmed booking on the same listing. total_price '
            'is calculated once (price * nights) and frozen — later '
            'price changes on the listing do not affect it.'
        ),
        examples=[
            OpenApiExample(
                '10-night stay',
                value={'listing': 1, 'start_date': '2026-09-01',
                       'end_date': '2026-09-11'},
                request_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=['Bookings'],
        summary='Booking detail',
        description='Visible to the tenant who made it, or the owner of the listing.',
    ),
)
class BookingViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/bookings/                — own bookings (tenant) or
                                               bookings on own listings (landlord)
    POST   /api/v1/bookings/                — create a booking (tenant only)
    GET    /api/v1/bookings/{id}/           — booking detail
    POST   /api/v1/bookings/{id}/confirm/   — confirm (listing owner only)
    POST   /api/v1/bookings/{id}/reject/    — reject (listing owner only)
    POST   /api/v1/bookings/{id}/cancel/    — cancel (tenant only)

    Direct editing of dates/status via PATCH/PUT is not allowed —
    status changes only happen through the explicit actions below,
    to prevent disallowed transitions (e.g. a tenant confirming
    their own booking)"""

    http_method_names = ['get', 'post', 'head', 'options']
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookingFilter

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(
            Q(tenant_id=user.pk) | Q(listing__owner_id=user.pk)
        ).select_related('listing', 'tenant')

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [drf_permissions.IsAuthenticated(), IsTenant()]
        if self.action in ('retrieve', 'confirm', 'reject', 'cancel'):
            return [drf_permissions.IsAuthenticated(), IsBookingTenantOrListingOwner()]
        return [drf_permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # tenant is set from request.user, status defaults to PENDING.
        serializer.save(tenant=self.request.user)

    @extend_schema(
        tags=['Bookings'],
        summary='Confirm a booking',
        description='Listing owner only. Only a PENDING booking can be confirmed.',
        request=None,
        responses={200: BookingSerializer, 400: None, 403: None}
    )
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        if booking.listing.owner_id != request.user.pk:
            return Response(
                {'detail': "Only the listing owner can confirm the reservation"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if booking.status != Booking.Status.PENDING:
            return Response(
                {'detail': "Only reservations with the status 'pending' can be confirmed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking.status = Booking.Status.CONFIRMED
        booking.save()
        return Response(BookingSerializer(booking).data)

    @extend_schema(
        tags=['Bookings'],
        summary='Reject a booking',
        description='Listing owner only. Only a PENDING booking can be rejected.',
        request=None,
        responses={200: BookingSerializer, 400: None, 403: None},
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        booking = self.get_object()
        if booking.listing.owner_id != request.user.pk:
            return Response(
                {'detail': "Only the listing owner can decline a reservation"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if booking.status != Booking.Status.PENDING:
            return Response(
                {'detail': "You can only cancel reservations with the status 'pending'"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking.status = Booking.Status.REJECTED
        booking.save()
        return Response(BookingSerializer(booking).data)

    @extend_schema(
        tags=['Bookings'],
        summary='Cancel a booking',
        description=(
            'Tenant only. Allowed for PENDING or CONFIRMED bookings, '
            'and only strictly before the start date — a booking that '
            'has already started can no longer be cancelled.'
        ),
        request=None,
        responses={200: BookingSerializer, 400: None, 403: None},
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.tenant_id != request.user.pk:
            return Response(
                {'detail': "Only the renter can cancel their reservation"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if booking.status not in (Booking.Status.PENDING, Booking.Status.CONFIRMED):
            return Response(
                {'detail': 'This reservation is no longer active'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Cancellation is only allowed in advance — not on or after the start date
        if booking.start_date <= timezone.localdate():
            return Response(
                {'detail': 'You can cancel your reservation only up until the check-in date.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking.status = Booking.Status.CANCELLED
        booking.save()
        return Response(BookingSerializer(booking).data)
