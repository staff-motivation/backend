from djoser.views import UserViewSet
from .serializers import CustomUserCreateSerializer, CustomUserRetrieveSerializer
from rest_framework import viewsets
from rest_framework import permissions
from users.models import User
from .permissions import CanEditOwnData, CanEditSkillsAndAchievements


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return CustomUserRetrieveSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]

        if self.action in ['retrieve', 'update', 'partial_update']:
            return [CanEditOwnData()]

        if self.action in ['list', 'destroy']:
            return [permissions.IsAuthenticated()]

        return super().get_permissions()
