from djoser.views import UserViewSet
from .serializers import CustomUserCreateSerializer, CustomUserRetrieveSerializer
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.decorators import action
from users.models import User
from tasks.models import Task
from .permissions import CanEditUserFields, IsTaskCreator, CanViewAllTasks, \
    CanCreateEditDeleteTasks, CanStartTask, CanCompleteTask, CanEditStatus

from .serializers import TaskSerializer, TaskStatusUpdateSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'list':
            return [CanViewAllTasks()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [CanCreateEditDeleteTasks()]
        elif self.action == 'start_task':
            return [CanStartTask()]
        elif self.action == 'complete_task':
            return [CanCompleteTask()]
        elif self.action == 'update_status':
            return [CanEditStatus()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        if not request.user.is_teamleader:
            return Response({"detail": "Задачи может создавать только Тимлид."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():

            serializer.validated_data['creator'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def start_task(self, request, pk=None):
        task = self.get_object()
        if not task.assignees.filter(pk=request.user.pk).exists():
            return Response({"detail": "Это не ваша задача."}, status=status.HTTP_403_FORBIDDEN)

        if task.status != 'created':
            return Response({"detail": "Задача еще не создана."}, status=status.HTTP_400_BAD_REQUEST)

        task.status = 'in_progress'
        task.start_date = timezone.now()
        task.save()
        return Response(TaskSerializer(task).data)

    @action(detail=True, methods=['post'])
    def complete_task(self, request, pk=None):
        task = self.get_object()
        if not request.user.is_teamleader:
            return Response({"detail": "Задачи может завершать только Тимлид.."}, status=status.HTTP_403_FORBIDDEN)

        status_data = request.data.get('status')
        if status_data not in ['completed', 'returned_for_revision']:
            return Response({"detail": "Неверный статус задачи"}, status=status.HTTP_400_BAD_REQUEST)

        task.status = status_data
        task.save()
        return Response(TaskSerializer(task).data)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

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