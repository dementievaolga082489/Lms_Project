from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from users.models import User


@shared_task
def deactivate_inactive_users() -> str:
    """Блокирует пользователей, не заходивших более 30 дней."""

    threshold = timezone.now() - timedelta(days=30)

    updated = (
        User.objects.filter(is_active=True)
        .filter(last_login__lt=threshold)
        .update(is_active=False)
    )
    return f"Заблокировано пользователей: {updated}"
