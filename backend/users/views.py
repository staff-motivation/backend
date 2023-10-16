from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from users.filters import UserFilter
from users.models import Achievement, User, UserAchievement
from users.permissions import (
    IsAnonymous,
    IsAuthenticated,
    IsOwnerOrTeamleader,
    IsTeamLeader,
)
from users.serializers import (
    CustomUserRetrieveSerializer,
    ShortUserProfileSerializer,
    UserImageSerializer,
)


@extend_schema_view(
    list=extend_schema(
        description='Получение списка пользователей.\n'
        '\nФильтрация по роли: /api/users/?role=admin\n'
        '\nФильтрация по должности: /api/users/?position=senior\n'
        '\nФильтрация по подразделению: /api/users/?department=Backend\n'
        '\nПоиск по email: /api/users/?email=user@example.com\n'
        '\nПоиск по имени: /api/users/?first_name=John\n'
        '\nПоиск по фамилии: /api/users/?last_name=Doe\n'
    ),
    create=extend_schema(description='Создание нового пользователя.'),
    retrieve=extend_schema(description='Получение пользователя по id.'),
    destroy=extend_schema(description='Удаление пользователя по id.'),
    update=extend_schema(
        description='Обновление пользователя по id.' ' Меняет объект целиком.'
    ),
    partial_update=extend_schema(
        description='Обновление пользователя по id.'
        ' Изменяет только переданные поля.'
    ),
)
class CustomDjUserViewSet(UserViewSet):
    """
    Overriding djoser's Users view
    """

    serializer_class = CustomUserRetrieveSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def get_permissions(self):
        if self.action == 'create':
            return [IsAnonymous()]
        if self.action in [
            'retrieve',
            'list',
            'update',
            'partial_update',
            'add_achievements',
        ]:
            return [IsTeamLeader()]
        if self.action == 'destroy':
            return [IsAdminUser()]
        if self.action == 'me':
            return [IsAuthenticated()]
        if self.action in ['delete_image', 'upload_image']:
            return [IsOwnerOrTeamleader]
        return super().get_permissions()

    def get_queryset(self):
        return User.objects.all()

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        """Получить информацию о себе."""
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Загрузка изображения для профиля пользователя."""
        user = self.get_object()
        serializer = UserImageSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_image(self, request, pk=None):
        """Удаление изображения профиля пользователя."""
        user = self.get_object()
        user.image.delete()
        user.image = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])
    def add_achievements(self, request, id):
        """Добавление достижений в профиль пользователя."""
        user = self.get_object()
        achievements_data = request.data.get('achievements', [])
        for achievement_data in achievements_data:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data['name'],
                value=achievement_data['value'],
                defaults={
                    'description': achievement_data.get('description', '')
                },
            )
            if 'image' in achievement_data:
                achievement.image = achievement_data['image']
            achievement.save()
            try:
                (
                    user_achievement,
                    created,
                ) = UserAchievement.objects.get_or_create(
                    user=user, achievement=achievement, defaults={}
                )
                if created:
                    user.reward_points = user.reward_points + achievement.value
                    user.reward_points_for_current_month = (
                        user.reward_points_for_current_month
                        + achievement.value
                    )
            except Exception:
                pass
        user.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(description='Получение информации пользователя для хедера.')
class ShortUserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShortUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)