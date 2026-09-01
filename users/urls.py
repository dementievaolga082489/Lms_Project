from django.urls import path
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import PaymentListView, UserCreateAPIView, UserViewSet, SubscriptionView, UserSubscriptionListView

app_name = UsersConfig.name

router = SimpleRouter()
router.register("users", UserViewSet, basename="user")


urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('login/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(permission_classes=(AllowAny,)), name='token_refresh'),
    path('subscriptions/toggle/', SubscriptionView.as_view(), name='subscription-toggle'),
    path('subscriptions/my/', UserSubscriptionListView.as_view(), name='my-subscriptions'),

]
urlpatterns += router.urls
