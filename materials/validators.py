import re
from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_youtube_link(value):
    """
    Функция-валидатор для проверки, что ссылка ведет на youtube.com
    """
    if not value:
        return value

    # Регулярное выражение для проверки YouTube ссылок
    youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$'

    if not re.match(youtube_pattern, value, re.IGNORECASE):
        raise ValidationError(
            'Разрешены только ссылки на YouTube'
        )

    return value