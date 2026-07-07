from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from listings.models import Listing


class Review(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        # один користувач не може залишити два відгуки на одну об'яву
        unique_together = ('listing', 'author')

    def __str__(self):
        return f'{self.listing} — {self.rating}/5'
