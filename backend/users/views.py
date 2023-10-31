from datetime import date

from dateutil.relativedelta import relativedelta  # type: ignore
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from tasks.models import Task
from users.filters import UserFilter
from users.models import Achievement, User, UserAchievement
from users.permissions import IsAnonymous, IsOwnerOrTeamleader, IsTeamLeader
from users.serializers import (
    CustomUserRetrieveSerializer,
    ProgressSerializer,
    ShortUserProfileSerializer,
    UploadUserImageSerializer,
)


class DisableUnusedEndpointsUserViewSet(UserViewSet):
    def set_password(self, request, *args, **kwargs):
        pass


@extend_schema(tags=['Users'])
@extend_schema_view(
    list=extend_schema(
        summary='Получение списка пользователей',
        description=(
            'Фильтрация по роли (role), по должности (position), по '
            'подразделению (department).\n\nПоиск по email, по имени '
            '(first_name), по фамилии (last_name)'
        ),
    ),
    create=extend_schema(summary='Создание нового пользователя.'),
    retrieve=extend_schema(summary='Получение пользователя по id.'),
    destroy=extend_schema(summary='Удаление пользователя по id.'),
    update=extend_schema(
        summary='Обновление пользователя по id.',
        description='Меняет объект целиком.',
    ),
    partial_update=extend_schema(
        summary='Обновление пользователя по id.',
        description='Изменяет только переданные поля.',
    ),
)
class CustomDjUserViewSet(DisableUnusedEndpointsUserViewSet):
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
        if self.action in ['me', 'progress']:
            return [IsAuthenticated()]
        if self.action in ['delete_image', 'upload_image']:
            return [IsOwnerOrTeamleader()]
        return super().get_permissions()

    def get_queryset(self):
        return User.objects.all()

    @extend_schema(summary='Получить информацию о себе.')
    @action(methods=['get'], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(summary='Получение прогресса пользователя')
    @action(methods=['get'], detail=False, serializer_class=ProgressSerializer)
    def progress(self, request):
        """
        Получение прогресса пользователя и его департамента за месяц.
        Значение в процентах от всех выполненных задач за месяц.
        """
        user = request.user
        today = date.today()
        start_of_month = today.replace(day=1)
        next_month = start_of_month + relativedelta(months=1)

        user_percentage = 0
        dep_percentage = 0

        total_approved_tasks_count = Task.objects.filter(
            deadline__gte=start_of_month,
            deadline__lt=next_month,
            status=Task.APPROVED,
        ).count()

        if total_approved_tasks_count > 0:
            user_approved_tasks_count = Task.objects.filter(
                deadline__gte=start_of_month,
                deadline__lt=next_month,
                assigned_to=user.id,
                status=Task.APPROVED,
            ).count()
            user_percentage = round(
                100 * (user_approved_tasks_count / total_approved_tasks_count)
            )

            department = user.department
            if department is not None:
                dep_approved_tasks_count = Task.objects.filter(
                    deadline__gte=start_of_month,
                    deadline__lt=next_month,
                    status=Task.APPROVED,
                    department=department,
                ).count()
                dep_percentage = round(
                    100
                    * (dep_approved_tasks_count / total_approved_tasks_count)
                )

        data = {
            'personal_progress': user_percentage,
            'department_progress': dep_percentage,
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid()
        return Response(serializer.data)

    @extend_schema(
        summary='Загрузка изображения для профиля пользователя.',
        responses=UploadUserImageSerializer,
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'image': {'type': 'string', 'format': 'binary'}
                },
            },
        },
    )
    @action(detail=True, methods=['post'])
    def upload_image(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UploadUserImageSerializer(user, data=request.data)
        if serializer.is_valid():
            if user.image:
                user.image.delete()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary='Удаление изображения профиля пользователя.')
    @action(detail=True, methods=['delete'])
    def delete_image(self, request, *args, **kwargs):
        user = self.get_object()
        user.image.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary='Добавление достижений в профиль пользователя.')
    @action(detail=True, methods=['patch'])
    def add_achievements(self, request, *args, **kwargs):
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
            (
                user_achievement,
                created,
            ) = UserAchievement.objects.get_or_create(
                user=user, achievement=achievement, defaults={}
            )
            if created:
                user.reward_points = user.reward_points + achievement.value
                user.reward_points_for_current_month = (
                    user.reward_points_for_current_month + achievement.value
                )

        user.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(summary='Получение информации пользователя для хедера.')
class ShortUserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShortUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
