from rest_framework import generics, viewsets

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


# Для курса используем ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseListView(generics.ListAPIView):
    """Вывод списка курсов с уроками"""

    queryset = Course.objects.all().prefetch_related("lessons")
    serializer_class = CourseSerializer


class CourseDetailView(generics.RetrieveAPIView):
    """Вывод детальной информации о курсе с уроками"""

    queryset = Course.objects.all().prefetch_related("lessons")
    serializer_class = CourseSerializer


# Для уроков используем Generic-классы
class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
