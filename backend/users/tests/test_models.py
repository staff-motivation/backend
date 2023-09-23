from django.db import IntegrityError
from django.test import TestCase
from users.models import (
    Achievement,
    Contact,
    Department,
    Hardskill,
    Position,
    User,
    UserAchievement,
    UserHardskill,
    UserRole,
)


class UserModelTest(TestCase):
    """
    Тестирование модели User.
    """

    @classmethod
    def setUpTestData(cls):
        department = Department.objects.create(
            name='Backend', description='Test department'
        )
        hardskill = Hardskill.objects.create(name='Python')
        User.objects.create(
            department=department,
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
        ).hardskills.add(hardskill)

    def test_field_labels(self):
        user = User.objects.get(id=1)
        labels = {
            'department': 'Подразделение',
            'email': 'Адрес электронной почты',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'password': 'Пароль',
            'role': 'Роль',
            'position': 'Уровень должности',
            'experience': 'Рабочий стаж в команде',
            'reward_points': 'Баллы',
            'is_staff': 'Является ли пользователь персоналом',
            'is_active': 'Активен ли пользователь',
        }

        for field, label in labels.items():
            with self.subTest(field=field):
                field_label = user._meta.get_field(field).verbose_name
                self.assertEqual(field_label, label)

    def test_str_method(self):
        user = User.objects.get(id=1)
        expected_str = 'User Userov'
        self.assertEqual(str(user), expected_str)

    def test_get_full_name_method(self):
        user = User.objects.get(id=1)
        expected_full_name = 'Userov User'
        self.assertEqual(user.get_full_name(), expected_full_name)

    def test_get_short_name_method(self):
        user = User.objects.get(id=1)
        expected_short_name = 'User'
        self.assertEqual(user.get_short_name(), expected_short_name)

    def test_departments(self):
        user = User.objects.get(id=1)
        self.assertEqual(user.department.name, 'Backend')
        self.assertEqual(user.department.description, 'Test department')

    def test_is_admin_property(self):
        user = User.objects.get(id=1)
        self.assertFalse(user.is_admin)

    def test_is_teamleader_property(self):
        user = User.objects.get(id=1)
        self.assertTrue(user.is_teamleader)

    def test_is_role_property(self):
        user = User.objects.get(id=1)
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_teamleader)


class DepartmentModelTest(TestCase):
    """
    Тестирование модели Department.
    """

    @classmethod
    def setUpTestData(cls):
        Department.objects.create(
            name='Test Department', description='Test description'
        )

    def test_name_field(self):
        department = Department.objects.get(id=1)
        name = department.name
        self.assertEqual(name, 'Test Department')

    def test_description_field(self):
        department = Department.objects.get(id=1)
        description = department.description
        self.assertEqual(description, 'Test description')

    def test_image_field_blank(self):
        department = Department.objects.get(id=1)
        image = department.image
        self.assertEqual(image, '')

    def test_str_method(self):
        department = Department.objects.get(id=1)
        expected_result = 'Test Department'
        self.assertEqual(str(department), expected_result)


class HardskillModelTest(TestCase):
    """
    Тестирование модели Hardskill.
    """

    @classmethod
    def setUpTestData(cls):
        Hardskill.objects.create(name='Test Hardskill')

    def test_name_field(self):
        hardskill = Hardskill.objects.get(id=1)
        name = hardskill.name
        self.assertEqual(name, 'Test Hardskill')

    def test_str_method(self):
        hardskill = Hardskill.objects.get(id=1)
        expected_result = 'Test Hardskill'
        self.assertEqual(str(hardskill.name), expected_result)


class UserHardskillModelTest(TestCase):
    """
    Тестирование модели UserHardskill.
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
        hardskill = Hardskill.objects.create(name='Test Hardskill')
        UserHardskill.objects.create(user=user, hardskill=hardskill)

    def test_user_field(self):
        user_hardskill = UserHardskill.objects.get(id=1)
        user = user_hardskill.user
        self.assertEqual(user.first_name, 'User')
        self.assertEqual(user.last_name, 'Userov')

    def test_hardskill_field(self):
        user_hardskill = UserHardskill.objects.get(id=1)
        hardskill = user_hardskill.hardskill
        self.assertEqual(hardskill.name, 'Test Hardskill')


class AchievementModelTest(TestCase):
    """
    Тестирование модели Achievement.
    """

    @classmethod
    def setUpTestData(cls):
        Achievement.objects.create(
            name='Test Achievement', value=10, description='Test Description'
        )

    def test_name_max_length(self):
        achievement = Achievement.objects.get(id=1)
        max_length = achievement._meta.get_field('name').max_length
        self.assertEquals(max_length, 255)

    def test_value_min_value(self):
        achievement = Achievement.objects.get(id=1)
        min_value = (
            achievement._meta.get_field('value').validators[0].limit_value
        )
        self.assertEquals(min_value, 1)

    def test_value_max_value(self):
        achievement = Achievement.objects.get(id=1)
        max_value = (
            achievement._meta.get_field('value').validators[1].limit_value
        )
        self.assertEquals(max_value, 100)

    def test_description_blank(self):
        achievement = Achievement.objects.get(id=1)
        description_blank = achievement._meta.get_field('description').blank
        self.assertTrue(description_blank)


class UserAchievementModelTest(TestCase):
    """
    Тестирование модели UserAchievement.
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
        achievement = Achievement.objects.create(
            name='Test Achievement', value=10
        )
        UserAchievement.objects.create(user=user, achievement=achievement)

    def test_unique_constraint(self):
        user = User.objects.get(id=1)
        achievement = Achievement.objects.get(id=1)
        with self.assertRaises(IntegrityError):
            UserAchievement.objects.create(user=user, achievement=achievement)


class ContactModelTest(TestCase):
    """
    Тестирование модели Contact.
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
        Contact.objects.create(
            user=user, contact_type='Email', link='test@mail.ru'
        )

    def test_contact_str_method(self):
        contact = Contact.objects.get(id=1)
        self.assertEqual(str(contact), 'User - Email: test@mail.ru')

    def test_contact_user_relation(self):
        user = User.objects.get(id=1)
        contact = Contact.objects.get(id=1)
        self.assertEqual(contact.user, user)

    def test_contact_type_field(self):
        contact = Contact.objects.get(id=1)
        self.assertEqual(contact.contact_type, 'Email')
        self.assertIsInstance(contact.contact_type, str)
        self.assertLessEqual(len(contact.contact_type), 50)

    def test_contact_link_field(self):
        contact = Contact.objects.get(id=1)
        self.assertEqual(contact.link, 'test@mail.ru')
        self.assertIsInstance(contact.link, str)
        self.assertLessEqual(len(contact.link), 255)
