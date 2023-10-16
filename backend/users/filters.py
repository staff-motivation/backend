import django_filters
from users.models import User


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'position': ['exact'],
            'department': ['exact'],
            'role': ['exact'],
            'email': ['icontains'],
            'first_name': ['icontains'],
            'last_name': ['icontains'],
        }
