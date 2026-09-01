from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.permissions import IsModerator, IsOwner
from .models import Course, Lesson
from .paginators import Paginator
from .serializers import CourseSerializer, LessonSerializer


# Для курса используем ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = Paginator

    def get_permissions(self):
        """
        Разделяем права по action (действиям)
        """
        if self.action == 'create':
            # Создание - только для авторизованных пользователей, НЕ модераторов
            # Модераторы НЕ МОГУТ создавать курсы
            self.permission_classes = [IsAuthenticated, ~IsModerator]

        elif self.action in ['update', 'partial_update']:
            # Обновление - для модераторов ИЛИ владельцев
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]

        elif self.action == 'destroy':
            # Удаление - только для владельцев (модераторы НЕ МОГУТ удалять)
            self.permission_classes = [IsAuthenticated, IsOwner]

        else:
            # Просмотр (list, retrieve) - доступен всем (включая неавторизованных)
            self.permission_classes = [AllowAny]

        return super().get_permissions()

    def perform_create(self, serializer):
        """
        При создании курса автоматически привязываем владельца
        """
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """
        Фильтруем queryset в зависимости от прав пользователя
        """
        # Если пользователь модератор - показывает все курсы
        if self.request.user and self.request.user.is_authenticated and \
                self.request.user.groups.filter(name='moderators').exists():
            return Course.objects.all().prefetch_related('lessons')

        # Если пользователь авторизован - показывает только свои курсы
        elif self.request.user and self.request.user.is_authenticated:
            return Course.objects.filter(owner=self.request.user).prefetch_related('lessons')

        # Неавторизованные видят все курсы (только чтение)
        return Course.objects.all().prefetch_related('lessons')


class CourseListView(generics.ListAPIView):
    """Вывод списка курсов с уроками"""

    queryset = Course.objects.all().prefetch_related("lessons")
    serializer_class = CourseSerializer
    pagination_class = Paginator


class CourseDetailView(generics.RetrieveAPIView):
    """Вывод детальной информации о курсе с уроками"""

    queryset = Course.objects.all().prefetch_related("lessons")
    serializer_class = CourseSerializer


# Для уроков используем Generic-классы
class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = Paginator

    def get_permissions(self):
        if self.request.method == 'POST':
            # Создание - только для авторизованных, НЕ модераторов
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        else:
            # Просмотр - для всех
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        При создании урока автоматически привязываем владельца
        """
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """
        Фильтруем queryset в зависимости от прав пользователя
        """
        # Если пользователь модератор - показывает все уроки
        if self.request.user and self.request.user.is_authenticated and \
                self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.all().select_related('course', 'owner')

        # Если пользователь авторизован - показывает только свои уроки
        elif self.request.user and self.request.user.is_authenticated:
            return Lesson.objects.filter(owner=self.request.user).select_related('course', 'owner')

        # Неавторизованные видят все уроки (только чтение)
        return Lesson.objects.all().select_related('course', 'owner')


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            # Обновление - для модераторов ИЛИ владельцев
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]

        elif self.request.method == 'DELETE':
            # Удаление - только для владельцев (модераторы НЕ МОГУТ удалять)
            self.permission_classes = [IsAuthenticated, IsOwner]

        else:
            # Просмотр - для всех
            self.permission_classes = [AllowAny]

        return super().get_permissions()

