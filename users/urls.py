from django.urls import path
from rest_framework.routers import SimpleRouter

from users.apps import UsersConfig
from users.views import PaymentListView, UserProfileViewSet

app_name = UsersConfig.name

router = SimpleRouter()
router.register("users", UserProfileViewSet)


urlpatterns = [

    path('payments/', PaymentListView.as_view(), name='payment-list'),
   ]
urlpatterns += router.urls
