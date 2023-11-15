import json

from datetime import datetime, timedelta, timezone

from core.utils import get_image_file
from django.db.models.fields.files import ImageFieldFile
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from users.models import User
from users.tests.factories import UserFactory


class UserTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        dt = datetime.now(timezone.utc) - timedelta(days=5)
        cls.client = APIClient()
        cls.user = UserFactory.create(experience=dt)
        cls.client_aut = APIClient()
        cls.client_aut.force_authenticate(user=cls.user)

    def test_create_user(self):
        """Проверка создания пользователя и получения токена"""
        user_object = UserFactory.stub()
        data_user = {
            'first_name': user_object.first_name,
            'last_name': user_object.last_name,
            'password': user_object.password,
            'email': user_object.email,
            'password_confirmation': user_object.password,
        }
        count = User.objects.count()
        response = self.client.post('/api/users/', data_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(
            response_content['first_name'], data_user['first_name']
        )
        self.assertEqual(response_content['last_name'], data_user['last_name'])
        self.assertEqual(response_content['email'], data_user['email'])
        self.assertEqual(User.objects.count(), count + 1)

        user = User.objects.get(email=user_object.email)
        user.is_active = True
        user.save()
        data_token = {
            'email': user_object.email,
            'password': user_object.password,
        }
        response = self.client.post('/api/token/login/', data_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertIn('auth_token', response_content)

    def test_me(self):
        """Информацию может получить только авторизированный пользователь"""
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client_aut.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_image(self):
        """Проверка добавления и удаления изображения профиля"""
        self.assertFalse(self.user.image)
        image_file = get_image_file()
        url = f'/api/users/{self.user.id}/upload_image/'
        response = self.client_aut.post(url, {'image': image_file})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(self.user.image, ImageFieldFile)

        url = f'/api/users/{self.user.id}/delete_image/'
        response = self.client_aut.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.user.image)

    def test_user_experience(self):
        """Проверка получения стажа в текстовом виде"""
        response = self.client_aut.get('/api/users/me/')
        response_content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_content['experience'], '5 дней')
        self.assertEqual(
            response_content['general_experience'], 'Меньше одного дня'
        )
