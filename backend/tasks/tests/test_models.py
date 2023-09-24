from datetime import datetime

from django.test import TestCase
from tasks.models import Task
from users.models import Position, User, UserRole


class TaskModelTest(TestCase):
    """
    Тестирование модели Task.
    """

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(
            email='test@mail.ru',
            first_name='User',
            last_name='Userov',
            password='password',
            role=UserRole.TEAMLEADER,
            position=Position.SENIOR,
            experience=1,
            reward_points=0,
            is_staff=True,
            is_active=True,
        )
        Task.objects.create(
            title='Тестовая задача',
            description='Описание',
            deadline=datetime.now(),
            reward_points=50,
            team_leader=user,
            assigned_to=user,
            status='created',
        )

    def test_field_labels(self):
        task = Task.objects.get(id=1)
        labels = {
            'title': 'title',
            'description': 'description',
            'deadline': 'deadline',
            'reward_points': 'reward points',
            'team_leader': 'team leader',
            'assigned_to': 'assigned to',
            'status': 'status',
        }
        for field, label in labels.items():
            with self.subTest(field=field):
                field_label = task._meta.get_field(field).verbose_name
                self.assertEqual(field_label, label)

    def test_reward_points_validators(self):
        task = Task.objects.get(id=1)
        min_value = (
            task._meta.get_field('reward_points').validators[0].limit_value
        )
        max_value = (
            task._meta.get_field('reward_points').validators[1].limit_value
        )
        self.assertEqual(min_value, 1)
        self.assertEqual(max_value, 100)

    def test_str_method(self):
        task = Task.objects.get(id=1)
        self.assertEqual(str(task), 'Тестовая задача')
