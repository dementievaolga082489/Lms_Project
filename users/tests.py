from django.urls import reverse
from rest_framework import status

from materials.models import Course
from users.models import Subscription, User
from rest_framework.test import APIClient, APITestCase


class SubscriptionTestCase(APITestCase):
    """Тесты для функционала подписок"""

    def setUp(self):
        """
        Подготовка тестовых данных
        """
        self.user = User.objects.create(
            email='user@example.com',
        )
        self.user.set_password('testpassword123')
        self.user.save()

        self.another_user = User.objects.create(
            email='another@example.com',
        )
        self.another_user.set_password('testpassword123')
        self.another_user.save()

        self.course = Course.objects.create(
            name='Test Course',
            owner=self.user
        )

        self.another_course = Course.objects.create(
            name='Another Course',
            owner=self.another_user
        )

        self.subscription_toggle_url = reverse('users:subscription-toggle')
        self.subscriptions_list_url = reverse('users:my-subscriptions')

        self.client = APIClient()

    def test_add_subscription_as_authenticated_user(self):
        """
        Тест добавления подписки авторизованным пользователем
        """
        self.client.force_authenticate(user=self.user)

        data = {'course_id': self.course.id}
        response = self.client.post(self.subscription_toggle_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_remove_subscription(self):
        """
        Тест удаления подписки
        """
        self.client.force_authenticate(user=self.user)

        # Сначала создаем подписку
        subscription = Subscription.objects.create(user=self.user, course=self.course)

        # Затем удаляем
        data = {'course_id': self.course.id}
        response = self.client.post(self.subscription_toggle_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_add_subscription_as_unauthenticated_user(self):
        """
        Тест добавления подписки неавторизованным пользователем (запрещено)
        """
        data = {'course_id': self.course.id}
        response = self.client.post(self.subscription_toggle_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())


    def test_add_subscription_twice(self):
        """
        Тест повторного добавления подписки (должна удалиться)
        """
        self.client.force_authenticate(user=self.user)

        # Первая подписка
        data = {'course_id': self.course.id}
        response1 = self.client.post(self.subscription_toggle_url, data)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response1.data['message'], 'Подписка добавлена')

        # Повторная подписка (должна удалить)
        response2 = self.client.post(self.subscription_toggle_url, data)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['message'], 'Подписка удалена')

    def test_get_user_subscriptions(self):
        """
        Тест получения списка подписок пользователя
        """
        self.client.force_authenticate(user=self.user)

        # Создаем несколько подписок
        Subscription.objects.create(user=self.user, course=self.course)
        Subscription.objects.create(user=self.user, course=self.another_course)

        response = self.client.get(self.subscriptions_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['course'], self.course.id)
        self.assertEqual(response.data[1]['course'], self.another_course.id)

    def test_get_user_subscriptions_unauthenticated(self):
        """
        Тест получения списка подписок неавторизованным пользователем
        """
        response = self.client.get(self.subscriptions_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_course_is_subscribed_field(self):
        """
        Тест поля is_subscribed в сериализаторе курса
        """
        self.client.force_authenticate(user=self.user)

        # Проверяем без подписки
        course_url = reverse('materials:course-detail', args=[self.course.id])
        response = self.client.get(course_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_subscribed'])

        # Добавляем подписку
        self.client.post(self.subscription_toggle_url, {'course_id': self.course.id})

        # Проверяем с подпиской
        response = self.client.get(course_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])
