from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """ User profile: view and edit (name, phone, etc) """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    """ 
    Registers a new user.
    Password is write-only, hashed via set_password; password
    confirmation is checked via a separate password2 field """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'password', 'password2',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError(
                {'password2': 'The passwords do not match.'}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    POST /api/v1/accounts/me/change-password/
    Not a ModelSerializer — there's no direct mapping to model fields
    here, old_password is checked against the current hash rather
    than being written directly.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password])
    repeat_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'The current password is incorrect')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['repeat_password']:
            raise serializers.ValidationError(
                {'repeat_password': 'The passwords do not match'}
            )
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()

        # Blacklist every outstanding refresh token for this user so a
        # leaked/stolen token stops working immediately after a
        # password change. Access tokens themselves can't be revoked
        # individually with simplejwt, but they're short-lived (5 hours)
        # and won't be refreshable once the refresh token is blacklisted.

        from rest_framework_simplejwt.token_blacklist.models import (
            BlacklistedToken,
            OutstandingToken,
        )

        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)

        return user
