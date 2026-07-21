from django.conf import settings
from django.db import models

from .managers import ActiveListingManager
from .validators import price_validator, rooms_validator


class Listing(models.Model):
    class PropertyType(models.TextChoices):
        APARTMENT = 'apartment', 'Wohnung'
        HOUSE = 'house', 'Haus'
        ROOM = 'room', 'Zimmer'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='listings',
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    city = models.CharField(max_length=100, db_index=True)
    address = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=price_validator,
        db_index=True,
        help_text='Price per night, in the platform currency (0.01–100000.00)',
    )
    rooms = models.PositiveSmallIntegerField(
        validators=rooms_validator,
        db_index=True,
        help_text='Number of rooms (1-20)'
    )
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.APARTMENT,
        db_index=True,
        help_text='Type of property: apartment, house or room'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Toggle to show/hide the listing without deleting it'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # objects — all records (admin panel), active — only active ones (public API)
    objects = models.Manager()
    active = ActiveListingManager()

    class Meta:
        ordering = ['-created_at']
        base_manager_name = 'objects'

    def __str__(self):
        return f'{self.title} ({self.city})'

    def is_owned_by(self, user):
        """Check whether this specific user owns the listing"""
        return self.owner_id == user.pk

    def save(self, *args, **kwargs):
        """Calls full_clean() before saving (see accounts.User.save)"""
        self.full_clean()
        super().save(*args, **kwargs)
