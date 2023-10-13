from api.permissions import CanEditUserFields
from django.db.models import Q
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
    IsOwnerOrReadOnly,
    IsOwnerOrTeamleader,
    IsTeamLeader,
)
from users.serializers import (
    AchievementsAddSerializer,
    AchievementSerializer,
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
    update=extend_schema(description='Обновление пользователя по id.'
                         ' Меняет объект целиком.'),
    partial_update=extend_schema(description='Обновление пользователя по id.'
                                 ' Изменяет только переданные поля.'),
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
                'retrieve', 'list', 'update', 'partial_update',
                'add_achievements']:
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

    @action(["get"], detail=False)
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

    @action(
        detail=True,
        methods=['patch'],
        serializer_class=AchievementsAddSerializer
    )
    def add_achievements(self, request, id):
        """Добавление достижений в профиль пользователя."""
        serializer = AchievementsAddSerializer(data=request.data)
        if serializer.is_valid():
            achievement = serializer.save()
            user = self.get_object()
            user.reward_points = user.reward_points + achievement.value
            user.reward_points_for_current_month = (
                user.reward_points_for_current_month
                + achievement.value
            )
            Response("Достижения добавлены.", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserRetrieveSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def get_queryset(self):
        """
        Фильтрация по роли: /api/users/?role=admin
        Фильтрация по должности: /api/users/?position=senior
        Фильтрация по подразделению: /api/users/?department=Backend
        Поиск по email: /api/users/?email=user@example.com
        Поиск по имени: /api/users/?first_name=John
        Поиск по фамилии: /api/users/?last_name=Doe
        """
        queryset = super().get_queryset()
        filters = Q()

        role = self.request.query_params.get('role')
        if role:
            filters &= Q(role=role)

        position = self.request.query_params.get('position')
        if position:
            filters &= Q(position=position)

        department = self.request.query_params.get('department')
        if department:
            filters &= Q(department=department)

        email = self.request.query_params.get('email')
        if email:
            filters &= Q(email__icontains=email)

        first_name = self.request.query_params.get('first_name')
        if first_name:
            filters &= Q(first_name__icontains=first_name)

        last_name = self.request.query_params.get('last_name')
        if last_name:
            filters &= Q(last_name__icontains=last_name)

        return queryset.filter(filters)

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]

        if self.action in ['retrieve', 'update', 'partial_update']:
            return [CanEditUserFields()]

        if self.action == 'list':
            return [permissions.IsAuthenticated()]

        if self.action in ['destroy']:
            return [IsAdminUser()]

        return super().get_permissions()

    def partial_update(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @extend_schema(description='Добавление достижений в профиль пользователя.')
    @action(detail=True, methods=['patch'], permission_classes=[IsTeamLeader])
    def add_achievements(self, request, pk=None):
        user = self.get_object()
        achievements_data = request.data.get('achievements', [])
        for achievement_data in achievements_data:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data['name'],
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

    @extend_schema(
        description='Загрузка изображения для профиля пользователя.'
    )
    @action(
        detail=True, methods=['post'], permission_classes=[IsOwnerOrReadOnly]
    )
    def upload_image(self, request, pk=None):
        user = self.get_object()
        serializer = UserImageSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description='Удаление изображения профиля пользователя.')
    @action(
        detail=True, methods=['delete'], permission_classes=[IsOwnerOrReadOnly]
    )
    def delete_image(self, request, pk=None):
        user = self.get_object()
        user.image.delete()
        user.image = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(description='Получение информации пользователя для хедера.')
class ShortUserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShortUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
