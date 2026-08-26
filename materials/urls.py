from django.urls import path
from rest_framework.routers import SimpleRouter

from materials.apps import MaterialsConfig
from materials.views import (CourseDetailView, CourseListView, CourseViewSet,
                             LessonListCreateView,
                             LessonRetrieveUpdateDestroyView)

app_name = MaterialsConfig.name

router = SimpleRouter()
router.register("courses", CourseViewSet, basename="course")


urlpatterns = [
    path("lessons/", LessonListCreateView.as_view(), name="lesson-list-create"),
    path(
        "lessons/<int:pk>/",
        LessonRetrieveUpdateDestroyView.as_view(),
        name="lesson-detail",
    ),
]
urlpatterns += router.urls
