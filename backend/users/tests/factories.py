from django.contrib.auth import get_user_model
from factory import Faker
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    password = Faker('password')
    is_active = True

    class Meta:
        model = User
