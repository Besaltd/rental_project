from django.contrib.auth.models import UserManager as DjangoUserManager


class UserManager(DjangoUserManager):
    """
    Custom manager for User.

    Inherits from the built-in Django UserManager (so create_user/
    create_superuser keep working as expected), but hides soft-deleted
    users from the default queryset
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
