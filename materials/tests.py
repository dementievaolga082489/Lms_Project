from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from materials.models import Course, Lesson
from users.models import User


class LessonCRUDTestCase(APITestCase):
    """Тесты для CRUD операций с уроками"""

    def setUp(self):
        """
        Подготовка тестовых данных
        """
        # Создаем пользователей
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

        # Создаем группу модераторов
        self.moderator_group, _ = Group.objects.get_or_create(name='moderators')
        self.moderator = User.objects.create(
            email='moderator@example.com',
        )
        self.moderator.set_password('testpassword123')
        self.moderator.save()
        self.moderator.groups.add(self.moderator_group)

        # Создаем курс
        self.course = Course.objects.create(
            name='Test Course',
            owner=self.user
        )

        # Создаем урок
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            course=self.course,
            owner=self.user
        )

        # URL для API
        self.lessons_list_url = reverse('materials:lesson-list-create')
        self.lesson_detail_url = reverse('materials:lesson-detail', args=[self.lesson.id])

        # Клиент для API
        self.client = APIClient()

    def test_create_lesson_as_authenticated_user(self):
        """
        Тест создания урока авторизованным пользователем (не модератором)
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'New Lesson',
            'course': self.course.id
        }

        response = self.client.post(self.lessons_list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().owner, self.user)
        self.assertEqual(Lesson.objects.last().name, 'New Lesson')

    def test_create_lesson_as_moderator(self):
        """
        Тест создания урока модератором (должен быть запрещен)
        """
        self.client.force_authenticate(user=self.moderator)

        data = {
            'name': 'Moderator Lesson',
            'course': self.course.id
        }

        response = self.client.post(self.lessons_list_url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)  # Урок не должен создаться

    def test_create_lesson_as_unauthenticated_user(self):
        """
        Тест создания урока неавторизованным пользователем (должен быть запрещен)
        """
        data = {
            'name': 'Unauth Lesson',
            'course': self.course.id
        }

        response = self.client.post(self.lessons_list_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Lesson.objects.count(), 1)  # Урок не должен создаться

    def test_list_lessons_as_user(self):
        """
        Тест получения списка уроков авторизованным пользователем
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.lessons_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Lesson')

    def test_list_lessons_as_moderator(self):
        """
        Тест получения списка уроков модератором (видит все уроки)
        """
        self.client.force_authenticate(user=self.moderator)

        # Создаем урок другого пользователя
        Lesson.objects.create(
            name='Another Lesson',
            course=self.course,
            owner=self.another_user
        )

        response = self.client.get(self.lessons_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Модератор видит все уроки


    def test_update_lesson_as_owner(self):
        """
        Тест обновления урока владельцем
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'Updated Lesson Name',
        }

        response = self.client.patch(self.lesson_detail_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, 'Updated Lesson Name')

    def test_update_lesson_as_moderator(self):
        """
        Тест обновления урока модератором (разрешено)
        """
        self.client.force_authenticate(user=self.moderator)

        data = {
            'name': 'Updated By Moderator',
        }

        response = self.client.patch(self.lesson_detail_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, 'Updated By Moderator')

    def test_update_lesson_as_another_user(self):
        """
        Тест обновления урока другим пользователем (запрещено)
        """
        self.client.force_authenticate(user=self.another_user)

        data = {
            'name': 'Hacked Lesson',
        }

        response = self.client.patch(self.lesson_detail_url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.lesson.refresh_from_db()
        self.assertNotEqual(self.lesson.name, 'Hacked Lesson')



    def test_delete_lesson_as_owner(self):
        """
        Тест удаления урока владельцем
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_as_moderator(self):
        """
        Тест удаления урока модератором (запрещено)
        """
        self.client.force_authenticate(user=self.moderator)

        response = self.client.delete(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_delete_lesson_as_another_user(self):
        """
        Тест удаления урока другим пользователем (запрещено)
        """
        self.client.force_authenticate(user=self.another_user)

        response = self.client.delete(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_retrieve_lesson_as_user(self):
        """
        Тест получения деталей урока пользователем
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Lesson')
        self.assertEqual(response.data['course'], self.course.id)

    def test_retrieve_lesson_as_moderator(self):
        """
        Тест получения деталей урока модератором
        """
        self.client.force_authenticate(user=self.moderator)

        response = self.client.get(self.lesson_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Lesson')