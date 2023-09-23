from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import (
    Achievement, Position, User, UserRole,
    UserAchievement
)
from tasks.models import Task


class TaskViewSetTestCase(TestCase):
    """
    Тестирование работы Задач.
    """

    def setUp(self):
        self.client = APIClient()
        self.team_leader = User.objects.create(
            email='team@mail.ru',
            first_name='Lid',
            last_name='Lidov',
            password='password',
            role=UserRole.TEAMLEADER,
            position=Position.SENIOR,
            experience=1,
            reward_points=0,
            is_staff=True,
            is_active=True,
        )
        self.executor = User.objects.create(
            email='test@mail.ru',
            first_name='User',
            last_name='Userov',
            password='password',
            role=UserRole.USER,
            position=Position.JUNIOR,
            experience=1,
            reward_points=0,
            is_staff=False,
            is_active=True,
        )
        self.task = self.task = Task.objects.create(
            title='Тестовая задача',
            description='Описание',
            deadline=datetime.now(),
            reward_points=50,
            team_leader=self.team_leader,
            assigned_to=self.executor,
            status='created'
        )

    def test_create_task_as_team_leader(self):
        """
        Тимлид создает задачу. Оk
        """
        self.client.force_authenticate(user=self.team_leader)
        response = self.client.post(
            'api/tasks',
            {
                "title": "Тестовая задача",
                "description": "Описание",
                "deadline": "2023-12-30 23:59",
                "reward_points": 300,
                "team_leader": 1,
                "assigned_to": 2,
                "status": "created"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        new_task = Task.objects.get(title='New Task')
        self.assertEqual(new_task.status, 'created')

    def test_create_task_as_non_team_leader(self):
        """
        Юзер создает задачу. 403 forbidden
        """
        self.client.force_authenticate(user=self.executor)
        response = self.client.post(
            'api/tasks',
            {
                'title': 'New Task',
                'description':'Описание',
                'reward_points':50,
                'team_leader':self.team_leader,
                'assigned_to':self.executor
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Task.objects.count(), 1)

    def test_send_task_for_review(self):
        """
        Отправка задачи на ревью. Ok
        """
        self.client.force_authenticate(user=self.executor)
        response = self.client.post(
            f'/api/tasks/{self.task.id}/send_for_review/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'sent_for_review')

    def test_send_task_for_review_with_invalid_status(self):
        """
        Отправка задачи с неверным статусом на ревью. 400 bad request
        """
        self.task.status = 'in_progress'
        self.task.save()
        self.client.force_authenticate(user=self.executor)
        response = self.client.post(
            f'/api/tasks/{self.task.id}/send_for_review/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'in_progress')

    def test_send_task_for_review_with_invalid_sender(self):
        """
        Отправка задачи на ревью НЕ исполнителем задачи. 403 forbidden
        """
        self.client.force_authenticate(user=self.team_leader)
        response = self.client.post(
            f'/api/tasks/{self.task.id}/send_for_review/'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'created')

    def test_review_task_approve(self):
        """
        Тимлид принимает задачу. Ok. 
        Увеличивается счетчик выполненных задач.
        Исполнителю начилсяются баллы за задачу.
        """
        self.client.force_authenticate(user=self.team_leader)
        response = self.client.post(
            f'/api/tasks/{self.task.id}/review_task/',
            {'status': 'approve'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'Принята и выполнена')
        assigned_user = self.task.assigned_to
        self.assertEqual(assigned_user.completed_tasks_count, 1)
        self.assertEqual(assigned_user.reward_points, self.task.reward_points)

    def test_review_task_reject(self):
        """
        Тимлид отправляет задачу на доработку. Ok
        """
        self.client.force_authenticate(user=self.team_leader)
        response = self.client.post(
            f'/api/tasks/{self.task.id}/review_task/',
            {'status': 'reject'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'Возвращена на доработку')

    def test_get_task_list(self):
        """
        Получить список задач. Ok
        """
        self.client.force_authenticate(user=self.executor)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tasks = response.json()
        self.assertEqual(len(tasks), 1)


class CustomUserViewSetTestCase(TestCase):
    """
    Тестирование функционала пользователя.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            email='test@mail.ru',
            first_name='User',
            last_name='Userov',
            password='password',
            role=UserRole.USER,
            position=Position.JUNIOR,
            experience=1,
            reward_points=0,
            is_staff=False,
            is_active=True,
        )
        self.user1 = User.objects.create(
            email='test1@mail.ru',
            first_name='User1',
            last_name='Userov1',
            password='password',
            role=UserRole.USER,
            position=Position.JUNIOR,
            experience=1,
            reward_points=0,
            is_staff=False,
            is_active=True,
        )
        self.user2 = User.objects.create(
            email='test2@mail.ru',
            first_name='User2',
            last_name='Userov2',
            password='password',
            role=UserRole.ADMIN,
            position=Position.MIDDLE,
            experience=1,
            reward_points=0,
            is_staff=False,
            is_active=True,
        )
        self.user3 = User.objects.create(
            email='test3@mail.ru',
            first_name='User3',
            last_name='Userov3',
            password='password',
            role=UserRole.TEAMLEADER,
            position=Position.SENIOR,
            experience=1,
            reward_points=0,
            is_staff=False,
            is_active=True,
        )

    # def test_filter_users_by_first_name(self):
    #     """
    #     Фильтрация пользователей по имени.
    #     """
    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.get('/api/users/?first_name=User')
    #     self.assertEqual(response.status_code, 200)
    #     usernames = [user['first_name'] for user in response.data]
    #     self.assertEqual(usernames, ['User', 'User1', 'User2'])
    
    # def test_filter_users_by_role(self):
    #     """
    #     Фильтрация пользователей по роли.
    #     """
    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.get('/api/users/?role=admin')
    #     self.assertEqual(response.status_code, 200)
    #     first_names = [user['first_name'] for user in response.data]
    #     self.assertEqual(first_names, ['User', 'User1'])
    
    # def test_filter_users_by_position(self):
    #     """
    #     Фильтрация пользователей по позиции.
    #     """
    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.get('/api/users/?position=senior')
    #     self.assertEqual(response.status_code, 200)
    #     first_names = [user['first_name'] for user in response.data]
    #     self.assertEqual(first_names, ['User3'])
    
    # def test_filter_users_by_email(self):
    #     """
    #     Фильтрация пользователей по email.
    #     """
    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.get('/api/users/?email=test2@mail.ru')
    #     self.assertEqual(response.status_code, 200)
    #     first_names = [user['first_name'] for user in response.data]
    #     self.assertEqual(first_names, ['User2'])


class AchievementViewSetTestCase(TestCase):
    """
    Тестирование добавления достижений пользователю.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            email='user@mail.ru',
            first_name='User',
            last_name='Userov',
            password='password',
            role=UserRole.USER,
            position=Position.JUNIOR,
            experience=1,
            reward_points=0,
            is_staff=False,
            is_active=True,
        )
        self.team_leader = User.objects.create(
            email='teamleader@mail.ru',
            first_name='Team',
            last_name='Leader',
            password='password',
            role=UserRole.TEAMLEADER,
            position=Position.SENIOR,
            experience=1,
            reward_points=0,
            is_staff=False,
            is_active=True,
        )
        self.non_team_leader = User.objects.create(
            email='nonteamleader@mail.ru',
            first_name='Team',
            last_name='Leader',
            password='password',
            role=UserRole.USER,
            position=Position.SENIOR,
            experience=1,
            reward_points=0,
            is_staff=False,
            is_active=True,
        )
        self.achievement = Achievement.objects.create(
            name='Achievement 1',
            value=10
        )

    def test_access_achievments_unauthorized_user(self):
        """
        Присваивание достижения неавторизованным пользователем
        """
        with self.assertRaises(PermissionDenied):
            UserAchievement.objects.create(
                user=self.user,
                achievement=self.achievement
        )

    def test_access_only_for_team_leader(self):
        """
        Присваивание достижения не тимлидом.
        """
        self.client.force_login(self.non_team_leader)
        with self.assertRaises(PermissionDenied):
            UserAchievement.objects.create(
                user=self.user,
                achievement=self.achievement
        )
