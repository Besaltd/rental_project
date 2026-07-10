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
    )
    rooms = models.PositiveSmallIntegerField(
        validators=rooms_validator,
        db_index=True,
    )
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.APARTMENT,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # objects — усі записи (для адмінкі)
    objects = models.Manager()
    # active — лише активні (для API)
    active = ActiveListingManager()

    class Meta:
        ordering = ['-created_at']
        base_manager_name = 'objects'

    def __str__(self):
        return f'{self.title} ({self.city})'

    def is_owned_by(self, user):
        """Перевірка власності обʼяви конкретним користувачем."""
        return self.owner_id == user.pk

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
