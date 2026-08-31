from django.conf import settings
from django.db import models

from users.models import User


class Course(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название курса",
        help_text="Введите название курса",
    )
    preview = models.ImageField(
        upload_to="materials/course_previews/",
        verbose_name="Превью курса",
        help_text="Загрузите картинку",
        blank=True,
        null=True,
    )
    description = models.TextField(
        verbose_name="Описание курса",
        help_text="Введите описание курса",
        blank=True,
        null=True,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец курса",
        related_name='courses',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название урока",
        help_text="Введите название урока",
    )
    description = models.TextField(
        verbose_name="Описание урока",
        help_text="Введите описание урока",
        blank=True,
        null=True,
    )
    preview = models.ImageField(
        verbose_name="Превью урока",
        help_text="Загрузите картинку урока",
        upload_to="materials/lesson_previews/",
        blank=True,
        null=True,
    )
    video_url = models.URLField(verbose_name="Ссылка на видео", blank=True, null=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс",
        help_text="Выберите курс",
        related_name="lessons",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец урока",
        related_name='lessons',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
