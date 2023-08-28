from djoser.views import UserViewSet
from .serializers import CustomUserCreateSerializer, CustomUserRetrieveSerializer
from rest_framework import viewsets

from users.models import User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserCreateSerializer
