from django.core.validators import MaxValueValidator, MinValueValidator

rating_validator = [
    MinValueValidator(1, message='The rating cannot be less than 1.'),
    MaxValueValidator(5, message='The rating cannot be greater than 5.'),
]
