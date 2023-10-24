from datetime import date

from dateutil.relativedelta import relativedelta
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import NotificationSerializer
from notifications.models import Notification
from tasks.models import Task


class ProgressUserAndDepartmentAPI(APIView):
    """API для получения прогресса пользователя и его департамента за месяц.
    Значение в процентах от всех выполненных задач за месяц."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()
        start_of_month = today.replace(day=1)
        next_month = start_of_month + relativedelta(months=1)

        department = user.department
        if department is None:
            return Response(
                {'error': 'У пользователя отсутствует департамент.'},
                status=status.HTTP_400_BAD_REQUEST,)
        total_approved_tasks_count = Task.objects.filter(
            deadline__gte=start_of_month,
            deadline__lt=next_month,
            status=Task.APPROVED
        ).count()
        if total_approved_tasks_count == 0:
            return Response(
                {'error': 'Нет выполненных задач в текущем месяце.'},
                status=status.HTTP_400_BAD_REQUEST,)
        user_approved_tasks_count = Task.objects.filter(
            deadline__gte=start_of_month,
            deadline__lt=next_month,
            assigned_to=user.id,
            status=Task.APPROVED
        ).count()
        dep_approved_tasks_count = Task.objects.filter(
            deadline__gte=start_of_month,
            deadline__lt=next_month,
            status=Task.APPROVED,
            department=department
        ).count()

        user_percentage = round(
            100 * (user_approved_tasks_count / total_approved_tasks_count))
        dep_percentage = round(
            100 * (dep_approved_tasks_count / total_approved_tasks_count))

        return Response({
            'personal_progress': user_percentage,
            'department_progress': dep_percentage,
        })


@extend_schema(description='Получение уведомлений пользователя.')
class UserNotificationsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user).order_by('-created_at')
