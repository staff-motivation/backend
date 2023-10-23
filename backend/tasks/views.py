import datetime

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from department.models import Department
from notifications.models import Notification
from tasks.models import Task
from tasks.permissions import IsTeamleader
from tasks.serializers import (TaskCreateSerializer, TaskReviewSerializer,
                               TaskSerializer)
from users.models import User


@extend_schema_view(
    list=extend_schema(
        description='Получение списка задач текущего'
        ' пользователя или тимлида.'
    ),
    retrieve=extend_schema(description='Получение задачи по id.'),
    destroy=extend_schema(description='Удаление задачи по id.'),
    update=extend_schema(
        description='Обновление задачи по id.' ' Меняет объект целиком.'
    ),
    partial_update=extend_schema(
        description='Обновление задачи по id.'
        ' Изменяет только переданные поля.'
    ),
)
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [IsTeamleader()]
        else:
            return super().get_permissions()

    @extend_schema(description='Обновление статуса просроченных задач.')
    def update_overdue_tasks(self):
        overdue_tasks = Task.objects.filter(
            deadline__lt=timezone.now(),
            status__in=[Task.CREATED, Task.RETURNED],
        )
        for task in overdue_tasks:
            task.is_overdue = True
            task.save()

    @extend_schema(description='Создание новой задачи тимлидером.')
    def create(self, request):
        serializer = TaskCreateSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            assigned_user_id = request.data.get('assigned_to')
            if assigned_user_id:
                department = Department.objects.get_or_create(
                    name=request.data.get('department')
                )
                task = serializer.save(department=department[0])
                assigned_user = User.objects.get(id=assigned_user_id)
                task.assigned_to = assigned_user
                task.save()
                Notification.objects.create(
                    user=assigned_user,
                    message=(
                        f'Вы были назначены исполнителем задачи "{task.title}"'
                    ),
                )
                return Response(
                    {'message': 'Задача успешно создана'},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {'error': 'Выберите хотя бы одного исполнителя'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        description=(
            'Отправка задачи текущего пользователя на проверку тимлидеру.'
        )
    )
    @action(detail=True, methods=['POST'], serializer_class=None)
    def send_for_review(self, request, pk=None):
        task = self.get_object()
        user = request.user

        if user == task.assigned_to:
            if task.status in [Task.CREATED, Task.RETURNED]:
                task.status = Task.SENT
                task.save()
                Notification.objects.create(
                    user=task.team_leader,
                    message=(
                        f'Задача "{task.title}" отправлена на проверку'
                        ' и ожидает вашей проверки'
                    ),
                )
                return Response({'status': 'Задача отправлена на проверку'})
            else:
                return Response(
                    {
                        'error': (
                            'Задачу можно отправить на проверку только со'
                            f' статусом "{Task.CREATED}" или "{Task.RETURNED}"'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {
                    'error': (
                        'Это не ваша задача или у вас нет прав '
                        'отправить ее на проверку'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        description='Проверка задачи тимлидом и изменение её статуса.'
    )
    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsTeamleader],
        serializer_class=TaskReviewSerializer,
    )
    def review_task(self, request, pk=None):
        task = self.get_object()
        if task.status == Task.APPROVED:
            return Response(
                {'error': 'Задача уже была принята и выполнена'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TaskReviewSerializer(data=request.data)
        if serializer.is_valid():
            review_status = serializer.validated_data['review_status']

            if review_status == Task.APPROVED:
                with transaction.atomic():
                    task.status = Task.APPROVED
                    task.save()
                    assigned_user = task.assigned_to
                    assigned_user.completed_tasks_count += 1
                    assigned_user.reward_points += task.reward_points
                    assigned_user.reward_points_for_current_month += (
                        task.reward_points
                    )
                    assigned_user.save()

                    Notification.objects.create(
                        user=task.team_leader,
                        message=(
                            f'Задача "{task.title}" была принята и выполнена'
                        ),
                    )
                    Notification.objects.create(
                        user=task.assigned_to,
                        message=(
                            f'Задача "{task.title}" была принята и выполнена'
                        ),
                    )
                return Response(
                    {'message': 'Принята и выполнена'},
                    status=status.HTTP_200_OK,
                )
            elif review_status == Task.RETURNED:
                task.status = Task.RETURNED
                task.save()
                Notification.objects.create(
                    user=task.team_leader,
                    message=(
                        f'Задача "{task.title}" была возвращена на доработку'
                    ),
                )

                Notification.objects.create(
                    user=task.assigned_to,
                    message=(
                        f'Задача "{task.title}" была возвращена на доработку'
                    ),
                )

                return Response(
                    {'message': 'Задача возвращена на доработку'},
                    status=status.HTTP_200_OK,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(description='Получение задач с фильтрацией.')
    def get_queryset(self):
        """
        Фильтрация задач по статусу и просроченным дедлайнам.
        Пример запроса с фильтрацией - Новые задачи:
        http://example.com/api/tasks/?status=createdx

        Пример запроса с фильтрацией - На подтверждении:
        http://example.com/api/tasks/?status=sent_for_review

        Пример запроса с фильтрацией - Просроченные:
        http://example.com/api/tasks/?is_overdue=true
        """
        self.update_overdue_tasks()
        queryset = Task.objects.filter(
            Q(assigned_to=self.request.user) | Q(team_leader=self.request.user)
        )
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        is_overdue = self.request.query_params.get('is_overdue')
        if is_overdue:
            queryset = queryset.filter(deadline__lt=datetime.date.today())

        return queryset
