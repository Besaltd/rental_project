from django.db import models


class ActiveListingManager(models.Manager):
    """Returns only active listings (is_active=True)"""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
