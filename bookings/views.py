from django.db.models import Q
from rest_framework import permissions as drf_permissions
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Booking
from .permissions import IsBookingTenantOrListingOwner, IsTenant
from .serializers import BookingCreateSerializer, BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):

    http_method_names = ['get', 'post', 'head', 'options']

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
        serializer.save(tenant=self.request.user)

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
        booking.status = Booking.Status.CANCELLED
        booking.save()
        return Response(BookingSerializer(booking).data)
