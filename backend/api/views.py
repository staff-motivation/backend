from djoser.views import UserViewSet
from .serializers import CustomUserCreateSerializer, CustomUserRetrieveSerializer
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.decorators import action
from users.models import User, Hardskill, Achievement, UserHardskill, UserAchievement
from tasks.models import Task, TaskUpdate, TaskInvitation, STATUS_CHOICES

from .permissions import CanEditUserFields, IsTaskCreator, CanViewAllTasks, \
    CanCreateEditDeleteTasks, CanStartTask, CanCompleteTask, CanEditStatus, IsTeamLeader

from .serializers import TaskSerializer, TaskUpdateSerializer, TaskInvitationSerializer, HardskillsSerializer, AchievementSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @action(detail=True, methods=['POST'])
    def invite_users(self, request, pk=None):
        task = self.get_object()
        invited_user_ids = request.data.get('invited_users', [])

        for user_id in invited_user_ids:
            user = User.objects.get(id=user_id)
            TaskInvitation.objects.create(task=task, user=user)

        return Response({"message": "Users invited successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def review_task(self, request, pk=None):
        task = self.get_object()
        user = self.request.user
        status = request.data.get('status', '')

        if status == 'approve':
            with transaction.atomic():
                TaskUpdate.objects.create(task=task, user=user, status='completed')
                user.reward_points += task.reward_points
                user.save()
            return Response({"message": "Task approved and completed"}, status=status.HTTP_200_OK)
        elif status == 'reject':
            TaskUpdate.objects.create(task=task, user=user, status='returned_for_revision')
            return Response({"message": "Task rejected"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def accept_invitation(self, request, pk=None):
        task = self.get_object()
        user = self.request.user

        invitation = get_object_or_404(TaskInvitation, task=task, user=user, accepted=False)
        invitation.accepted = True
        invitation.save()

        task.assigned_to.add(user)
        return Response({"message": "User accepted the invitation and joined the task"}, status=status.HTTP_200_OK)


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