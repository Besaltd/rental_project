from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.utils import timezone
from .validators import phone_validator
from .managers import UserManager


class User(AbstractUser):

    class Role(models.TextChoices):
        TENANT = 'tenant', 'Mieter'
        LANDLORD = 'landlord', 'Vermieter'

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TENANT,
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator],
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()
    all_objects = DjangoUserManager()

    class Meta:
        base_manager_name = 'all_objects'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    @property
    def is_landlord(self):
        return self.role == self.Role.LANDLORD

    @property
    def is_tenant(self):
        return self.role == self.Role.TENANT

    def owns(self, obj):
        owner_field = getattr(obj, 'owner_id', None) or getattr(
            obj, 'tenant_id', None)
        return owner_field == self.pk

    def can_review(self, booking):
        from bookings.models import Booking

        if booking.tenant_id != self.pk:
            return False
        if booking.status != Booking.Status.CONFIRMED:
            return False
        if hasattr(booking, 'review'):
            return False
        return True

    def delete(self, using=None, keep_parents=False):
        # М'яке видалення: позначає користувача як видаленого.
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['is_deleted', 'deleted_at', 'is_active'])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
