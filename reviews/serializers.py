from rest_framework import serializers

from accounts.serializers import UserSerializer
from bookings.models import Booking

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Full review info for reading"""
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
    """
    Creating a review as a tenant.
    booking is accepted as an id, author and listing are set in the
    view automatically (author = request.user, listing = booking.listing)
    """

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


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Editing an existing review (PATCH).
    Intentionally only allows changing rating/comment — booking,
    listing, author are NOT writable, otherwise someone could swap
    which booking/listing a review belongs to
    """
    class Meta:
        model = Review
        fields = ['id', 'booking', 'listing', 'author', 'rating', 'comment']
        read_only_fields = ['id', 'booking', 'listing', 'author']
