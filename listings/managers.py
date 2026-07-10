from django.db import models


class ActiveListingManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
