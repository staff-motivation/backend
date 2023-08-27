from djoser.views import UserViewSet
from .serializers import CustomUserCreateSerializer, CustomUserRetrieveSerializer
from users.models import User
from rest_framework.decorators import action


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserRetrieveSerializer