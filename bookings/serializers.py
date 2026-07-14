from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from listings.models import Listing
from listings.serializers import ListingSerializer

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):

    listing = ListingSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'tenant', 'start_date', 'end_date',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'tenant',
                            'status', 'created_at', 'updated_at']


class BookingCreateSerializer(serializers.ModelSerializer):

    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.active.all())

    class Meta:
        model = Booking
        fields = ['id', 'listing', 'start_date', 'end_date']
        read_only_fields = ['id']

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


# class BookingStatusUpdateSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Booking
#         fields = ['id', 'status']
#         read_only_fields = ['id']
