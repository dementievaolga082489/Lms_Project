from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course
from users.services import (create_stripe_price, create_stripe_product,
                            create_stripe_session)

from .models import Payments, Subscription, User
from .permissions import IsOwner
from .serializers import (PaymentSerializer, PaymentStripeSerializer,
                          SubscriptionSerializer, UserProfileSerializer,
                          UserPublicSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """CRUD для пользователей"""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "create":
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
        if self.action in ["update", "partial_update"]:
            # Редактирование только своего профиля
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action == "destroy":
            # Удаление только своего профиля
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            # Просмотр доступен авторизованным
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            # Для операций с конкретным объектом проверяем права в permission
            return User.objects.all()
        # Для списка показываем только себя
        if self.request.user.is_authenticated:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.none()

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
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


class SubscriptionView(APIView):
    """
    APIView для управления подписками пользователя на курсы
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Переключает подписку пользователя на курс.
        Если подписка есть - удаляет, если нет - создает.
        """
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "Необходимо указать course_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Получаем объект курса или возвращаем 404
        course = get_object_or_404(Course, id=course_id)

        # Проверяем существование подписки
        subscription = Subscription.objects.filter(
            user=user, course=course, is_active=True
        )

        if subscription.exists():
            # Если подписка существует - удаляем (деактивируем)
            subscription.delete()
            message = "Подписка удалена"
            status_code = status.HTTP_200_OK
        else:
            # Если подписки нет - создаем
            Subscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"
            status_code = status.HTTP_201_CREATED

        return Response({"message": message}, status=status_code)


class UserSubscriptionListView(APIView):
    """
    Получение списка подписок текущего пользователя
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscriptions = Subscription.objects.filter(user=request.user, is_active=True)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)


class PaymentCreateApiView(CreateAPIView):
    """
    ViewSet для управления платежами с интеграцией Stripe
    """

    queryset = Payments.objects.all()
    serializer_class = PaymentStripeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    search_fields = ["user__email", "course__name"]
    ordering_fields = ["payment_date", "amount"]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Создание платежа с интеграцией Stripe
        """
        # Сохраняем платеж с текущим пользователем
        payment = serializer.save(user=self.request.user)

        # Валидация: должен быть выбран курс ИЛИ урок, но не оба
        if payment.course is None and payment.lesson is None:
            raise ValidationError("Необходимо выбрать курс или урок")

        if payment.course and payment.lesson:
            raise ValidationError("Необходимо выбрать либо курс, либо урок")

        # Определяем объект для оплаты (курс или урок)
        if payment.course:
            product_name = payment.course.name
            product_description = payment.course.description or ""
        else:
            product_name = payment.lesson.name
            product_description = payment.lesson.description or ""

        # 1. Создаем продукт в Stripe
        product = create_stripe_product(product_name, product_description)

        # 2. Создаем цену в Stripe (сумма в копейках)
        price = create_stripe_price(payment.amount, product.id)

        # 3. Создаем сессию оплаты
        session = create_stripe_session(price.id)

        # 4. Сохраняем данные от Stripe в платеже
        payment.stripe_product_id = product.id
        payment.stripe_price_id = price.id
        payment.stripe_session_id = session.id
        payment.payment_url = session.url
        payment.save()
