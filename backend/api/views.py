import datetime
from django.db.models import Q

from notifications.models import Notification
from .serializers import CustomUserRetrieveSerializer, ShortUserProfileSerializer, NotificationSerializer
from rest_framework import viewsets, status
from rest_framework import permissions, filters
from rest_framework.decorators import action
from users.models import User, Hardskill, Achievement, UserAchievement
from tasks.models import Task, TaskUpdate, TaskInvitation
from .permissions import CanEditUserFields, IsTeamLeader

from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction


class UserNotificationsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user).order_by('-created_at')


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            task = serializer.save()

            invited_user_ids = request.data.get('assigned_to', [])
            for user_id in invited_user_ids:
                user = User.objects.get(id=user_id)
                TaskInvitation.objects.create(task=task, user=user)

                Notification.objects.create(
                    user=user,
                    message=f'Вы были приглашены в задачу "{task.title}"'
                )

            return Response({"message": "Задача успешно создана"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def list_tasks(self, request):
        if request.user.is_authenticated:
            tasks = self.queryset.filter(Q(assigned_to=request.user) | Q(team_leader=request.user))
            task_data = []
            for task in tasks:
                task_data.append({
                    'title': task.title,
                    'description': task.description,
                    'deadline': task.deadline,
                    'reward_points': task.reward_points,
                    'status': task.status
                })
            return Response({'tasks': task_data})
        else:
            return Response({'error': 'Неавторизованный пользователь'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['POST'])
    def accept_task(self, request, pk=None):
        task = self.get_object()
        user = request.user

        if user in task.assigned_to.all():
            task.status = 'in_progress'
            task.save()
            Notification.objects.create(
                user=user,
                message=f'Задача "{task.title}" принята, статус изменен на "in_progress"'
            )

            Notification.objects.create(
                user=task.team_leader,
                message=f'Задача "{task.title}" была принята сотрудником {user.first_name}'
            )

            invitation = get_object_or_404(TaskInvitation, task=task, user=user, accepted=False)
            invitation.accepted = True
            invitation.save()

            task.assigned_to.add(user)

            return Response({'status': 'Сотрудник принял задачу, ее статус изменен на "in_progress"'})
        else:
            return Response({'error': 'Это не ваша задача'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def invite_users(self, request, pk=None):
        task = self.get_object()
        invited_user_ids = request.data.get('invited_users', [])

        for user_id in invited_user_ids:
            user = User.objects.get(id=user_id)
            TaskInvitation.objects.create(task=task, user=user)

            Notification.objects.create(
                user=user,
                message=f'Вы были приглашены в задачу "{task.title}"'
            )

        return Response({"message": "Сотрудники добавлены в задачу"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def review_task(self, request, pk=None):
        task = self.get_object()
        user = self.request.user
        review_status = request.data.get('status', '')

        if task.status == 'Принята и выполнена':
            return Response({"error": "Задача уже была принята и выполнена"}, status=status.HTTP_400_BAD_REQUEST)

        if review_status == 'approve':
            with transaction.atomic():
                task.status = 'Принята и выполнена'
                task.save()
                TaskUpdate.objects.create(task=task, user=user, status='completed')
                for assigned_user in task.assigned_to.all():
                    assigned_user.reward_points += task.reward_points
                    assigned_user.save()

                for assigned_user in task.assigned_to.all():
                    Notification.objects.create(
                        user=assigned_user,
                        message=f'Задача "{task.title}" была принята и выполнена'
                    )

            return Response({"message": "Принята и выполнена"}, status=status.HTTP_200_OK)
        elif review_status == 'reject':
            task.status = 'Возвращена на доработку'
            task.save()
            TaskUpdate.objects.create(task=task, user=user, status='returned_for_revision')

            for assigned_user in task.assigned_to.all():
                Notification.objects.create(
                    user=assigned_user,
                    message=f'Задача "{task.title}" была возвращена на доработку'
                )

            return Response({"message": "Задача возвращена на доработку"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Неверный статус"}, status=status.HTTP_400_BAD_REQUEST)

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
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('role', 'position')
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

    @action(detail=True, methods=['patch'], permission_classes=[IsTeamLeader])
    def add_hardskills(self, request, pk=None):
        user = self.get_object()
        hardskills_data = request.data.get('hardskills', [])

        for hardskill_data in hardskills_data:
            hardskill, created = Hardskill.objects.get_or_create(name=hardskill_data['name'])
            user.hardskills.add(hardskill)

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShortUserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShortUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)