from rest_framework.routers import SimpleRouter

from users.apps import UsersConfig
from users.views import UserProfileViewSet

app_name = UsersConfig.name

router = SimpleRouter()
router.register("users", UserProfileViewSet)


urlpatterns = []
urlpatterns += router.urls
