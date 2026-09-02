from rest_framework import serializers

from users.models import Subscription
from .models import Course, Lesson
from .validators import validate_youtube_link


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(
        validators=[validate_youtube_link],
        required=False,
        allow_blank=True,
        allow_null=True
    )

    class Meta:
        model = Lesson
        fields = ["id", "name", "description", "preview", "video_url", "course", "owner"]
        read_only_fields = ["owner"]


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Course с выводом уроков"""

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = ["id", "name", "preview", "description", "lessons_count", "lessons", "is_subscribed", "owner"]
        read_only_fields = ["owner"]

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на этот курс"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False
