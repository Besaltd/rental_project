from django.conf import settings
from django.db import models


class Listing(models.Model):
    class PropertyType(models.TextChoices):
        APARTMENT = 'apartment', 'Wohnung'
        HOUSE = 'house', 'Haus'
        ROOM = 'room', 'Zimmer'
    # кожна об'ява належить конкретному користувачу-власнику
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        # видаляє об'яви при видаленні користувача
        on_delete=models.CASCADE,
        related_name='listings',
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.PositiveSmallIntegerField()
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.APARTMENT,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.city})'
