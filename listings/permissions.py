from rest_framework import permissions


class IsLandlord(permissions.BasePermission):
    """Allows the action only to users with the 'landlord' role"""

    message = "Only 'landlords' can post listings"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_landlord)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """ Reading is allowed for everyone. Editing/deleting — owner only """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.is_owned_by(request.user)
