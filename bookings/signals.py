import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Booking

logger = logging.getLogger('bookings')


@receiver(pre_save, sender=Booking)
def stash_previous_status(sender, instance, **kwargs):

    if instance.pk:
        try:
            instance._previous_status = Booking.objects.get(
                pk=instance.pk).status
        except Booking.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Booking)
def log_status_change(sender, instance, created, **kwargs):
    if created:
        logger.info(
            'Booking #%s created: status=%s, listing=%s, tenant=%s',
            instance.pk, instance.status, instance.listing_id, instance.tenant_id,
        )
        return

    previous = getattr(instance, '_previous_status', None)
    if previous is not None and previous != instance.status:
        logger.info(
            'Booking #%s status changed: %s -> %s (listing=%s, tenant=%s)',
            instance.pk, previous, instance.status, instance.listing_id, instance.tenant_id,
        )
        # from .notifications import send_status_change_email
        # send_status_change_email(instance, previous_status=previous)
