from rest_framework import permissions


class IsTenant(permissions.BasePermission):

    message = "Only 'tenants' can make reservations"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_tenant)


class IsBookingTenantOrListingOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        return obj.tenant_id == user.pk or obj.listing.owner_id == user.pk
