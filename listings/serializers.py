from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Listing


class ListingSerializer(serializers.ModelSerializer):
    """
    Full listing info for reading (list and detail).
    owner is shown as a nested object (read-only) — the listing's
    owner cannot be changed through this field, only read
    """

    owner = UserSerializer(read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'owner', 'title', 'description', 'city', 'address',
            'price', 'rooms', 'property_type', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ListingWriteSerializer(serializers.ModelSerializer):
    """
    Creating/editing a listing.
    owner is not accepted from the frontend here — it's set in the
    view from request.user (so nobody can create a listing on
    someone else's behalf)
    """

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'city', 'address',
            'price', 'rooms', 'property_type', 'is_active',
        ]
        read_only_fields = ['id']
