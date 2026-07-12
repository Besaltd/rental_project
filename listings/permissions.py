from rest_framework import permissions


class IsLandlord(permissions.BasePermission):

    message = "Only 'landlords' can post listings"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_landlord)


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.is_owned_by(request.user)
