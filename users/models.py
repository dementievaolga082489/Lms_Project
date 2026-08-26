from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from materials.models import Course, Lesson


class User(AbstractBaseUser):
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
        User,
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
        Course,
        on_delete=models.CASCADE,
        verbose_name="Оплаченный курс",
        null=True,
        blank=True,
        related_name='payments',
    )
    lesson = models.ForeignKey(
        Lesson,
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
