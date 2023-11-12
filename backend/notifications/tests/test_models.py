from django.test import TestCase

from notifications.models import Notification
from users.models import Position, User, UserRole


class NotificationModelTest(TestCase):
    """
    Тестирование модели Notification.
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
        Notification.objects.create(user=user, message='Тестовое уведомление')

    def test_field_labels(self):
        notification = Notification.objects.get(id=1)
        labels = {'user': 'user', 'message': 'message'}
        for field, label in labels.items():
            with self.subTest(field=field):
                field_label = notification._meta.get_field(field).verbose_name
                self.assertEqual(field_label, label)

    def test_read_field_default_value(self):
        notification = Notification.objects.get(id=1)
        read = notification.read
        self.assertFalse(read)

    def test_str_method(self):
        notification = Notification.objects.get(id=1)
        expected_result = 'Тестовое уведомление'
        self.assertEqual(str(notification), expected_result)
