from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "name", "description", "preview", "video_url", "course"]


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Course с выводом уроков"""

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = ["id", "name", "preview", "description", "lessons_count", "lessons"]
