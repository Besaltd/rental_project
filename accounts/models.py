from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models
from django.utils import timezone
from .validators import phone_validator
from .managers import UserManager


class User(AbstractUser):
    """
    Custom user model.

    Inherits from AbstractUser -> keeps standard fields
    (username, password, first_name, last_name, is_active, etc.)
    Adds project-specific fields: role, phone, soft delete.
    """

    class Role(models.TextChoices):
        TENANT = 'tenant', 'Mieter'
        LANDLORD = 'landlord', 'Vermieter'

    email = models.EmailField(
        unique=True,
        help_text='Used as the login identifier'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TENANT,
        help_text=(
            'tenant: can browse and book listings. landlord: can create '
            'and manage listings. Set at registration, editable via '
            'PATCH /accounts/me/ afterwards'
        ),
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator],
        help_text='7 to 15 digits, optionally starting with "+"'
    )

    # The spec requires login via email + password (not username).
    # simplejwt automatically picks up USERNAME_FIELD and renames
    # the field in the body of POST /api/v1/auth/token/ from "username"
    # to "email"
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Soft delete: deleting a user does not remove the row from the DB,
    # it only marks it as deleted (so we don't lose the history of
    # bookings/listings linked to this user)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # `objects` is the default manager and hides deleted users
    # `all_objects` gives unfiltered access (e.g. for the admin panel)
    objects = UserManager()
    all_objects = DjangoUserManager()

    class Meta:
        base_manager_name = 'all_objects'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

    @property
    def is_landlord(self):
        """Whether the user has the landlord (Vermieter) role"""
        return self.role == self.Role.LANDLORD

    @property
    def is_tenant(self):
        """Whether the user has the tenant (Mieter) role"""
        return self.role == self.Role.TENANT

    def owns(self, obj):
        """
        Check whether this user owns the given object
        (Listing, Booking, etc). `obj` must have an `owner` or
        `tenant` field.
        """
        owner_field = getattr(obj, 'owner_id', None) or getattr(
            obj, 'tenant_id', None)
        return owner_field == self.pk

    def can_review(self, booking):
        """
        Check whether this user is allowed to leave a review for
        a given booking. All conditions must be true:
            - the user is the tenant on this booking
            - the booking status is CONFIRMED
            - the stay is actually over (end_date has passed) —
            otherwise a review could be left before the tenant even
            moved in
            - no review has been left for this booking yet
        """
        from bookings.models import Booking
        from django.utils import timezone

        if booking.tenant_id != self.pk:
            return False
        if booking.status != Booking.Status.CONFIRMED:
            return False
        if booking.end_date >= timezone.localdate():
            return False
        if hasattr(booking, 'review'):
            return False
        return True

    def delete(self, using=None, keep_parents=False):
        """Soft delete: marks the user as deleted"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['is_deleted', 'deleted_at', 'is_active'])

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently removes the row from the database"""
        super().delete(using=using, keep_parents=keep_parents)

    def save(self, *args, **kwargs):
        """
        Explicitly calls full_clean() before saving — Django does NOT
        do this automatically in save(), and our validators (phone
        regex, unique email, etc) would otherwise only run through
        admin forms
        """
        self.full_clean()
        super().save(*args, **kwargs)
