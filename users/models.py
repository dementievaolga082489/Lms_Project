from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True, verbose_name="Почта", help_text="Укажите почту"
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Укажите телефон",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Укажите город",
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        help_text="Загрузите аватар",
        upload_to="users/avatars/",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payments(models.Model):
    """Модель платежи"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Выберите пользователя",
        related_name='payments'
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата платежа",
    )
    course = models.ForeignKey(
        'materials.Course',
        on_delete=models.CASCADE,
        verbose_name="Оплаченный курс",
        null=True,
        blank=True,
        related_name='payments',
    )
    lesson = models.ForeignKey(
        'materials.Lesson',
        on_delete=models.CASCADE,
        verbose_name="Оплаченный урок",
        null=True,
        blank=True,
        related_name = 'payments',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
        help_text="Укажите сумму оплаты",

    )
    payment_method = models.CharField(
        max_length=20,
        choices=[("cash", "Наличные"), ("transfer", "Перевод на счет")],
        verbose_name="Способ оплаты",
        help_text="Выберите способ оплаты",
    )

    def __str__(self):
        return f"{self.user.email} - {self.amount} ({self.payment_method})"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]


class Subscription(models.Model):
    """Модель подписки на обновления курса"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Пользователь, подписанный на обновления",
        related_name='subscriptions'
    )
    course = models.ForeignKey(
        'materials.Course',
        on_delete=models.CASCADE,
        verbose_name="Курс",
        help_text="Курс, на который подписан пользователь",
        related_name='subscribers'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
        help_text="Активна ли подписка"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.email} подписан на {self.course.name}"