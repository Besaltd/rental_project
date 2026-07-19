from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field

from listings.models import Listing
from listings.serializers import ListingSerializer

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):

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
        return obj.status == Booking.Status.CONFIRMED and obj.end_date < timezone.localdate()


class BookingCreateSerializer(serializers.ModelSerializer):

    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.active.all())

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'start_date', 'end_date', 'total_price']
        read_only_fields = ['id', 'total_price']

    def validate(self, attrs):
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
