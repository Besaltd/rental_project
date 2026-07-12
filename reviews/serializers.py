from rest_framework import serializers

from accounts.serializers import UserSerializer
from bookings.models import Booking

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'listing', 'booking', 'author', 'rating',
            'comment', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'listing',
                            'author', 'created_at', 'updated_at']


class ReviewCreateSerializer(serializers.ModelSerializer):

    booking = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all())

    class Meta:
        model = Review
        fields = ['id', 'booking', 'rating', 'comment']
        read_only_fields = ['id']

    def validate_booking(self, booking):
        user = self.context['request'].user
        if not user.can_review(booking):
            raise serializers.ValidationError(
                "You cannot leave a review for this reservation"
            )
        return booking
