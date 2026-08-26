from rest_framework import serializers

from .models import Payments, User


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Payments"""

    user_email = serializers.ReadOnlyField(source="user.email")
    course_name = serializers.ReadOnlyField(source="course.name", allow_null=True)
    lesson_name = serializers.ReadOnlyField(source="lesson.name", allow_null=True)

    class Meta:
        model = Payments
        fields = [
            "id",
            "user",
            "user_email",
            "payment_date",
            "course",
            "course_name",
            "lesson",
            "lesson_name",
            "amount",
            "payment_method",
        ]
        read_only_fields = ["user"]


class UserPaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежей в профиле пользователя"""

    course_name = serializers.ReadOnlyField(source="course.name", allow_null=True)
    lesson_name = serializers.ReadOnlyField(source="lesson.name", allow_null=True)

    class Meta:
        model = Payments
        fields = [
            "id",
            "payment_date",
            "course_name",
            "lesson_name",
            "amount",
            "payment_method",
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя с историей платежей"""

    payment_history = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "phone", "city", "avatar", "payment_history"]

    def get_payment_history(self, obj):
        """Получение истории платежей пользователя"""
        payments = obj.payments.all().order_by("-payment_date")
        return UserPaymentSerializer(payments, many=True).data
