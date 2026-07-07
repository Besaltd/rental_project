from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        TENANT = 'tenant', 'Mieter'
        LANDLORD = 'landlord', 'Vermieter'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TENANT,
    )
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    @property
    def is_landlord(self):
        return self.role == self.Role.LANDLORD

    @property
    def is_tenant(self):
        return self.role == self.Role.TENANT
