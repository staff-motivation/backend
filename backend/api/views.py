from datetime import date

from dateutil.relativedelta import relativedelta
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import (
    NotificationSerializer,
    ProgressSerializer,
    ErrorSerializer,
)
from notifications.models import Notification
from tasks.models import Task


class ProgressUserAndDepartmentAPI(GenericAPIView):
    """
    API для получения прогресса пользователя и его департамента за месяц.
    Значение в процентах от всех выполненных задач за месяц.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProgressSerializer

    @extend_schema(responses={
        status.HTTP_200_OK: ProgressSerializer,
        status.HTTP_401_UNAUTHORIZED: ErrorSerializer})
    def get(self, request):
        user = request.user
        today = date.today()
        start_of_month = today.replace(day=1)
        next_month = start_of_month + relativedelta(months=1)

        user_percentage = 0
        dep_percentage = 0

        total_approved_tasks_count = Task.objects.filter(
            deadline__gte=start_of_month,
            deadline__lt=next_month,
            status=Task.APPROVED
        ).count()

        if total_approved_tasks_count > 0:
            user_approved_tasks_count = Task.objects.filter(
                deadline__gte=start_of_month,
                deadline__lt=next_month,
                assigned_to=user.id,
                status=Task.APPROVED
            ).count()
            user_percentage = round(
                100 * (user_approved_tasks_count / total_approved_tasks_count))

            department = user.department
            if department is not None:
                dep_approved_tasks_count = Task.objects.filter(
                    deadline__gte=start_of_month,
                    deadline__lt=next_month,
                    status=Task.APPROVED,
                    department=department
                ).count()
                dep_percentage = round(
                    100 * (dep_approved_tasks_count /
                           total_approved_tasks_count))

        data = {
            'personal_progress': user_percentage,
            'department_progress': dep_percentage,
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid()
        return Response(serializer.data)


@extend_schema(description='Получение уведомлений пользователя.')
class UserNotificationsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user).order_by('-created_at')
