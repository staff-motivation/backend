from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.serializers import (
    NotificationSerializer,
    ProgressUserAndDepartmentSerializer,
)
from notifications.models import Notification
from users.models import User


@extend_schema(
    description=(
        'Получение прогресса достижений '
        'пользователя и информации о департаменте.'
    )
)
class ProgressUserAndDepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProgressUserAndDepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(pk=user.pk)
        return queryset


@extend_schema(description='Получение уведомлений пользователя.')
class UserNotificationsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user).order_by('-created_at')
