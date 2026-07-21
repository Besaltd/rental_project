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
    start_date = models.DateField(
        help_text='Check-on date (must not be in the past)')
    end_date = models.DateField(
        help_text='Check-out date (must be after start_date)'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        help_text=(
            'pending: awaiting owner decision. confirmed: accepted by owner'
            'rejected: declined by owner. cancelled: cancelled by tenant'
        ),
    )
    # Snapshot of listing.price * number of nights, calculated once
    # when the booking is created. Deliberately NOT recalculated from
    # listing.price afterwards — if the owner changes the price later,
    # past and pending bookings must keep the price the tenant actually
    # agreed to
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        help_text='listing.price * number of nights, frozen at creation time'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        """
        Booking validation: valid date range, no back-dated creation,
        and no overlap with other "live" bookings for the same listing
        """
        if self.end_date <= self.start_date:
            raise ValidationError(
                'The end date must be later than the start date.')

        # Cannot create a booking with a start date in the past.
        # Only checked on creation (self.pk is None) — editing an
        # existing booking with a past date (e.g. a completed stay)
        # should not break
        if self.pk is None and self.start_date < timezone.localdate():
            raise ValidationError('The start date cannot be in the past')

        if self.tenant_id is not None and self.listing.owner_id == self.tenant_id:
            raise ValidationError('You cannot book your own listing')

        # The overlap check only considers "live" bookings (not
        # cancelled or rejected) for the same listing.
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
        """
        Calculates total_price on first save (creation only), then
        calls full_clean() before saving (see accounts.User.save)
        """
        if self.pk is None:
            nights = (self.end_date - self.start_date).days
            self.total_price = self.listing.price * Decimal(nights)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.listing} — {self.start_date} → {self.end_date}'
