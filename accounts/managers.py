from django.contrib.auth.models import UserManager as DjangoUserManager


class UserManager(DjangoUserManager):

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
