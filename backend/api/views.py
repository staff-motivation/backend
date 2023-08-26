from djoser.views import UserViewSet
from .serializers import CustomUserCreateSerializer

from api.serializers import CustomUserCreateSerializer
from users.models import User


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserCreateSerializer