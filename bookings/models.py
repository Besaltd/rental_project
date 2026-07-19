from django.conf import settings
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from listings.models import Listing


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ausstehend'
        CONFIRMED = 'confirmed', 'Bestätigt'
        REJECTED = 'rejected', 'Abgelehnt'
        CANCELLED = 'cancelled', 'Storniert'

    listing = models.ForeignKey(
        Listing,
        on_delete=models.PROTECT,
        related_name='bookings',
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='bookings',
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError(
                'The end date must be later than the start date.')

        if self.pk is None and self.start_date < timezone.localdate():
            raise ValidationError('The start date cannot be in the past')

        overlapping = Booking.objects.filter(
            listing=self.listing,
            status__in=[self.Status.PENDING, self.Status.CONFIRMED],
        ).exclude(pk=self.pk).filter(
            start_date__lt=self.end_date,
            end_date__gt=self.start_date,
        )
        if overlapping.exists():
            raise ValidationError(
                'There are already reservations for these dates (pending confirmation or confirmed).'
            )

    def save(self, *args, **kwargs):

        if self.pk is None:
            nights = (self.end_date - self.start_date).days
            self.total_price = self.listing.price * Decimal(nights)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.listing} — {self.start_date} → {self.end_date}'
