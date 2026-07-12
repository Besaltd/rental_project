from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Listing


class ListingSerializer(serializers.ModelSerializer):

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

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'city', 'address',
            'price', 'rooms', 'property_type', 'is_active',
        ]
        read_only_fields = ['id']
