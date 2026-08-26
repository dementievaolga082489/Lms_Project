from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter

from .models import Payments, User
from .serializers import PaymentSerializer, UserProfileSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


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
