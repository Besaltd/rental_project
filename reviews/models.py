from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from bookings.models import Booking
from listings.models import Listing

from .validators import rating_validator


class Review(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviews',
    )
    booking = models.OneToOneField(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviews',
    )
    rating = models.PositiveSmallIntegerField(validators=rating_validator)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        # Автор відгуку має бути орендарем саме цього бронювання.
        if self.booking_id and self.booking.tenant_id != self.author_id:
            raise ValidationError(
                'Only the renter who made this reservation can leave a review.'
            )
        if self.booking_id and self.booking.status != Booking.Status.CONFIRMED:
            raise ValidationError(
                'You can only leave a review for a confirmed reservation.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        listing_title = self.listing.title if self.listing_id else 'deleted ad'
        return f'{listing_title} — {self.rating}/5'
