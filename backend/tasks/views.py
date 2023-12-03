import datetime

from datetime import date

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
from tasks.schema import task_schema
from tasks.serializers import (
    TaskCreateSerializer,
    TaskReviewSerializer,
    TaskSerializer,
)
from users.models import Achievement, User, UserAchievement


@extend_schema(tags=['Tasks'])
@extend_schema_view(**task_schema.task)
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [IsTeamleader()]
        else:
            return super().get_permissions()

    def update_overdue_tasks(self):
        overdue_tasks = Task.objects.filter(
            deadline__lt=timezone.now(),
            status__in=[Task.CREATED, Task.RETURNED],
        )
        for task in overdue_tasks:
            task.is_overdue = True
            task.save()

    def create(self, request):
        serializer = TaskCreateSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            assigned_user_id = request.data.get('assigned_to')
            if assigned_user_id:
                department, _ = Department.objects.get_or_create(
                    name=request.data.get('department')
                )
                task = serializer.save(department=department)
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

                    self.assign_achivements(assigned_user)

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

    def get_queryset(self):
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

    def assign_achivements(self, user):
        """
        Назначение достижений при изменении статуса задачи на \"Принято\".
        """
        current_year = date.today().year
        current_month = date.today().month
        try:
            achieve_work_quality = Achievement.objects.get(
                name='Качество работы'
            )
        except Achievement.DoesNotExist:
            return
        tasks_count = Task.objects.filter(
            assigned_to=user.id,
            deadline__month=current_month,
            deadline__year=current_year,
            status=Task.APPROVED,
            is_overdue=False,
        ).count()
        if tasks_count >= 30:
            _, created = UserAchievement.objects.get_or_create(
                user=user,
                achievement=achieve_work_quality,
            )
            if created:
                user.reward_points += achieve_work_quality.value
                user.reward_points_for_current_month += (
                    achieve_work_quality.value
                )
                user.save()
