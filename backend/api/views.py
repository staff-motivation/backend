from djoser.views import UserViewSet
from .serializers import CustomUserCreateSerializer

from api.serializers import (
    CustomUserCreateSerializer,
    CustomUserRetrieveSerializer
)
from users.models import User


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserCreateSerializer

    def get_serializer_class(self):
        if self.action in ['retrieve', 'me']:
            return CustomUserRetrieveSerializer
        return self.serializer_class