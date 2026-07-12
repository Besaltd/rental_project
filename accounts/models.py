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

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # `objects` — менеджер за замовчуванням, приховує видалених користувачів.
    # `all_objects` — доступ без фільтрації (наприклад, для адмінки).
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
        """
        Перевірка, чи є користувач власником обʼєкта
        (Listing, Booking тощо). obj повинен мати поле owner або tenant.
        """
        owner_field = getattr(obj, 'owner_id', None) or getattr(
            obj, 'tenant_id', None)
        return owner_field == self.pk

    def can_review(self, booking):
        """
        Перевірка, чи може користувач залишити відгук на бронювання.
        Усі умови мають бути істинними:
        - користувач є орендарем саме цього бронювання
        - статус бронювання CONFIRMED (проживання дійсно відбулось)
        - відгук на це бронювання ще не залишений
        """
        from bookings.models import Booking

        if booking.tenant_id != self.pk:
            return False
        if booking.status != Booking.Status.CONFIRMED:
            return False
        if hasattr(booking, 'review') and booking.review is not None:
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
