from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field

from listings.models import Listing
from listings.serializers import ListingSerializer

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    """
    Full booking info for reading.
    listing is shown as a nested object, tenant — id only
    (to avoid pulling the full tenant profile where it's not needed).
    """
    listing = ListingSerializer(read_only=True)
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'tenant', 'start_date', 'end_date',
            'status', 'is_completed', 'created_at', 'updated_at', 'total_price',
        ]
        read_only_fields = ['id', 'tenant', 'total_price',
                            'status', 'created_at', 'updated_at']

    @extend_schema_field(serializers.BooleanField)
    def get_is_completed(self, obj):
        # Derived flag (not a DB field): a confirmed booking whose
        # end date has already passed
        return obj.status == Booking.Status.CONFIRMED and obj.end_date < timezone.localdate()


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Creating a booking as a tenant.
    listing is accepted as an id (PrimaryKeyRelatedField), tenant
    is set in the view from request.user, status is always PENDING
    on creation (only the owner can confirm)
    """
    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.active.all())

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'start_date', 'end_date', 'total_price']
        read_only_fields = ['id', 'total_price']

    def validate(self, attrs):
        # The model itself checks date overlap and range validity
        # in Booking.clean(), but here we catch Django's ValidationError
        # and convert it to a format DRF understands
        booking = Booking(
            listing=attrs['listing'],
            tenant=self.context['request'].user,
            start_date=attrs['start_date'],
            end_date=attrs['end_date'],
        )
        try:
            booking.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict if hasattr(exc, 'message_dict') else exc.messages)
        return attrs
