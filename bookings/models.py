from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from listings.models import Listing


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ausstehend'
        CONFIRMED = 'confirmed', 'Bestätigt'
        REJECTED = 'rejected', 'Abgelehnt'
        CANCELLED = 'cancelled', 'Storniert'
    """ два користувача, чия обʼява та хто бронює """
    listing = models.ForeignKey(
        Listing,
        # видаляє бронювання разом з об'явою
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError(
                'Дата закінчення має бути пізніше дати початку.')

    def __str__(self):
        return f'{self.listing} — {self.start_date} → {self.end_date}'
