import datetime
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from notifications.models import Notification
from .serializers import CustomUserRetrieveSerializer, ShortUserProfileSerializer, NotificationSerializer, \
    UserImageSerializer, ProgressUserAndDepartmentSerializer
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.decorators import action
from users.models import User, Achievement, UserAchievement
from tasks.models import Task
from .permissions import IsOrdinaryUser, CanEditUserFields, IsTeamLeader, IsOwnerOrReadOnly

from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db import transaction


@extend_schema(description="Получение прогресса достижений пользователя и информации о департаменте.")
class ProgressUserAndDepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProgressUserAndDepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(pk=user.pk)
        return queryset


@extend_schema(description="Получение уведомлений пользователя.")
class UserNotificationsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user).order_by('-created_at')


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrdinaryUser]

    @extend_schema(description="Обновление статуса просроченных задач.")
    def update_overdue_tasks(self):
        overdue_tasks = self.queryset.filter(
            deadline__lt=timezone.now(),
            status__in=['created', 'returned_for_revision'])
        for task in overdue_tasks:
            task.status = 'Просрочена'
            task.save()

    @extend_schema(description="Получение списка задач с дополнительными данными.")
    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.update_overdue_tasks()
            tasks = self.queryset.filter(
                Q(assigned_to=request.user) | Q(team_leader=request.user))
            task_data = []
            for task in tasks:
                task_data.append({
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'deadline': task.deadline,
                    'reward_points': task.reward_points,
                    'status': task.status,
                    'assigned_to': task.assigned_to.get_full_name(),
                    'created_by': task.team_leader.get_full_name()
                })
            return Response({'tasks': task_data})
        else:
            return Response({'error': 'Неавторизованный пользователь'}, status=status.HTTP_401_UNAUTHORIZED)

    @extend_schema(description="Создание новой задачи тимлидером.")

    def create(self, request):
        if not request.user.is_teamleader:
            return Response({"error": "Доступ запрещен, создание задачи доступно только Тимлидерам"}, status=status.HTTP_403_FORBIDDEN)

        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            assigned_user_id = request.data.get('assigned_to')
            if assigned_user_id:
                task = serializer.save(status='created')
                assigned_user = User.objects.get(id=assigned_user_id)
                task.assigned_to = assigned_user
                task.save()
                Notification.objects.create(
                    user=assigned_user,
                    message=f'Вы были назначены исполнителем задачи "{task.title}"'
                )
                return Response({"message": "Задача успешно создана"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Выберите хотя бы одного исполнителя"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description="Отправка задачи на проверку тимлидеру.")
    @action(detail=True, methods=['POST'])
    def send_for_review(self, request, pk=None):
        task = self.get_object()
        user = request.user

        if user == task.assigned_to:
            if task.status in ['created', 'returned_for_revision']:
                task.status = 'sent_for_review'
                task.save()
                Notification.objects.create(
                    user=task.team_leader,
                    message=f'Задача "{task.title}" отправлена на проверку и ожидает вашей проверки'
                )
                return Response({'status': 'Задача отправлена на проверку'})
            else:
                return Response(
                    {
                        'error': 'Задачу можно отправить на проверку только со статусом "created" или "returned_for_revision"'},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Это не ваша задача или у вас нет прав отправить ее на проверку'},
                            status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description="Проверка задачи тимлидом и изменение её статуса.")
    @action(detail=True, methods=['POST'])
    def review_task(self, request, pk=None):
        if not request.user.is_teamleader:
            return Response({"error": "Доступ запрещен, завершение задачи доступно только Тимлидерам"}, status=status.HTTP_403_FORBIDDEN)

        task = self.get_object()
        user = self.request.user
        review_status = request.data.get('status', '')

        if task.status == 'Принята и выполнена':
            return Response({"error": "Задача уже была принята и выполнена"}, status=status.HTTP_400_BAD_REQUEST)

        if review_status == 'approve':
            with transaction.atomic():
                task.status = 'Принята и выполнена'
                task.save()
                assigned_user = task.assigned_to
                assigned_user.completed_tasks_count += 1
                assigned_user.save()
                assigned_user.reward_points += task.reward_points
                assigned_user.save()

                Notification.objects.create(
                    user=task.team_leader,
                    message=f'Задача "{task.title}" была принята и выполнена'
                )
                Notification.objects.create(
                    user=task.assigned_to,
                    message=f'Задача "{task.title}" была принята и выполнена'
                )
            return Response({"message": "Принята и выполнена"}, status=status.HTTP_200_OK)
        elif review_status == 'reject':
            task.status = 'Возвращена на доработку'
            task.save()
            Notification.objects.create(
                user=task.team_leader,
                message=f'Задача "{task.title}" была возвращена на доработку'
            )

            Notification.objects.create(
                user=task.assigned_to,
                message=f'Задача "{task.title}" была возвращена на доработку'
            )

            return Response({"message": "Задача возвращена на доработку"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Неверный статус"}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description="Получение задач с фильтрацией.")
    def get_queryset(self):
        """
        Фильтрация задач по статусу и просроченным дедлайнам.
        Пример запроса с фильтрацией - Новые задачи:
        http://example.com/api/tasks/?status=created

        Пример запроса с фильтрацией - В работе:
        http://example.com/api/tasks/?status=in_progress

        Пример запроса с фильтрацией - На подтверждении:
        http://example.com/api/tasks/?status=sent_for_review

        Пример запроса с фильтрацией - Просроченные:
        http://example.com/api/tasks/?is_overdue=true
        """
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        is_overdue = self.request.query_params.get('is_overdue')
        if is_overdue:
            queryset = queryset.filter(deadline__lt=datetime.date.today())
        
        return queryset


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserRetrieveSerializer

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
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @extend_schema(description="Добавление достижений в профиль пользователя.")
    @action(detail=True, methods=['patch'], permission_classes=[IsTeamLeader])
    def add_achievements(self, request, pk=None):
        user = self.get_object()
        achievements_data = request.data.get('achievements', [])

        for achievement_data in achievements_data:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults={'description': achievement_data.get('description', '')}
            )
            if 'image' in achievement_data:
                achievement.image = achievement_data['image']
            achievement.save()

            UserAchievement.objects.update_or_create(
                user=user,
                achievement=achievement,
                defaults={}
            )
            user.reward_points += achievement.value
            user.save()

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(description="Загрузка изображения для профиля пользователя.")
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrReadOnly])
    def upload_image(self, request, pk=None):
        user = self.get_object()
        serializer = UserImageSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description="Удаление изображения профиля пользователя.")
    @action(detail=True, methods=['delete'], permission_classes=[IsOwnerOrReadOnly])
    def delete_image(self, request, pk=None):
        user = self.get_object()
        user.image.delete()
        user.image = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(description="Получение информации пользователя для хедера.")
class ShortUserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShortUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)