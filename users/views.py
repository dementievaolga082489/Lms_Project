from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Payments, User
from .permissions import IsOwner
from .serializers import PaymentSerializer, UserProfileSerializer, UserSerializer, UserPublicSerializer


class UserViewSet(viewsets.ModelViewSet):
    """CRUD для пользователей"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            # Регистрация доступна для неавторизованных
            self.permission_classes = [AllowAny]
        else:
            # Остальные действия - только для авторизованных
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            # Редактирование только своего профиля
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action == 'destroy':
            # Удаление только своего профиля
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            # Просмотр доступен авторизованным
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Для операций с конкретным объектом проверяем права в permission
            return User.objects.all()
        # Для списка показываем только себя
        if self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            # Для просмотра других профилей используем публичный сериализатор
            return UserPublicSerializer
        # Для редактирования своего профиля используем полный
        return UserProfileSerializer


class PaymentListView(generics.ListAPIView):
    """Вывод списка платежей с фильтрацией и сортировкой"""

    queryset = Payments.objects.all().select_related("user", "course", "lesson")
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date", "amount"]
    ordering = ["-payment_date"]


class UserProfileView(generics.RetrieveAPIView):
    """Профиль пользователя с историей платежей"""

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "id"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("payments")
