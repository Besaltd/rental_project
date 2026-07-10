from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{7,15}$',
    message='A phone number must contain between 7 and 15 digits; it does not have to start with a “+”.',
)
