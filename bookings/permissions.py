from rest_framework import permissions


class IsTenant(permissions.BasePermission):
    """Allows the action only to users with the 'tenant' role"""

    message = "Only 'tenants' can make reservations"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_tenant)


class IsBookingTenantOrListingOwner(permissions.BasePermission):
    """
    Viewing/acting on a specific booking is allowed only to:
        - the tenant who created it
        - the owner of the listing this booking is for
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.tenant_id == user.pk or obj.listing.owner_id == user.pk
