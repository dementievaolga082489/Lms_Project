from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from users.models import Subscription


@shared_task
def send_course_update_email(course_id: int, course_name: str) -> str:
    """Рассылка письма подписчикам курса об обновлении материалов."""

    emails = list(
        Subscription.objects.filter(course_id=course_id, is_active=True)
        .select_related("user")
        .values_list("user__email", flat=True)
    )

    if not emails:
        return f"Курс {course_id}: подписчиков нет"

    send_mail(
        subject=f"Курс «{course_name}» обновлён",
        message=(f"Материалы курса «{course_name}» были обновлены."),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails,
        fail_silently=False,
    )
    return f"Курс {course_id}: письмо отправлено {len(emails)} подписчикам"
