from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

price_validator = [
    MinValueValidator(
        Decimal('0.01'), message='The price must be greater than zero.'),
    MaxValueValidator(Decimal('100000.00'),
                      message='The price cannot exceed 100,000.')
]

rooms_validator = [
    MinValueValidator(1, message='The number of rooms must be at least 1.'),
    MaxValueValidator(15, message='The number of rooms cannot exceed 15.'),
]
