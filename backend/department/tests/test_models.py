from department.models import Department
from django.test import TestCase


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
