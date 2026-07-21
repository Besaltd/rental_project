from rest_framework import permissions


class IsReviewAuthorOrReadOnly(permissions.BasePermission):
    """Reading is allowed for everyone. Editing/deleting — author only"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author_id == request.user.pk
