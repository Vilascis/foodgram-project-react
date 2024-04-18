from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


def validate_me_name(value):
    """Проверка имени пользователя на me"""
    invalid_username = ['me', 'set_password', 'subscriptions', 'subscribe']
    if value.lower() in invalid_username:
        raise ValidationError(
            (f'Нельзя использовать "{value}" в качасте имени пользователя!'),
        )
    return value


class UsernameValidator(UnicodeUsernameValidator):
    """Валидация имени пользователя."""

    message = 'Недопустимые символы в имени пользователя!'
