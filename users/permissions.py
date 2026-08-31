from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsModerator(BasePermission):
    """
    Проверка, является ли пользователь модератором.
    Модератор может просматривать и редактировать любые уроки и курсы,
    но не может удалять и создавать новые.
    """

    def has_permission(self, request, view):
        # Проверяем, авторизован ли пользователь
        if not request.user or not request.user.is_authenticated:
            return False

        # Проверяем, состоит ли пользователь в группе модераторов
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(BasePermission):
    """Проверка, является ли пользователь владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        # Проверяем, авторизован ли пользователь
        if not request.user or not request.user.is_authenticated:
            return False

        # Проверяем, является ли пользователь владельцем объекта
        return obj.owner == request.user

    def has_permission(self, request, view):
        # Для создания объекта проверяем только авторизацию
        return request.user and request.user.is_authenticated

    