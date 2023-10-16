from calendar import monthrange
from datetime import date
from math import floor

from dateutil.relativedelta import relativedelta  # type: ignore
from django.db import models
from notifications.models import Notification
from rest_framework import serializers
from tasks.models import Task
from users.models import User


class ProgressUserAndDepartmentSerializer(serializers.ModelSerializer):
    personal_progress = serializers.SerializerMethodField()
    department_progress = serializers.SerializerMethodField()
    total_reward_points_in_organization = serializers.SerializerMethodField()
    progress_for_deadline = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'personal_progress',
            'department_progress',
            'total_reward_points_in_organization',
            'progress_for_deadline',
        ]

    def get_metrics(self, obj):
        today = date.today()
        start_of_month = today.replace(day=1)
        end_of_month = today + relativedelta(
            day=31, hour=23, minute=59, second=59, microsecond=999999
        )
        current_year, current_month = today.year, today.month
        days_in_month = monthrange(current_year, current_month)[1]
        is_overdue = Task.objects.filter(
            is_overdue=True,
            deadline__month=current_month,
            deadline__year=current_year,
            assigned_to=obj.id,
        ).exists()
        tasks_count = Task.objects.filter(
            deadline__month=current_month,
            deadline__year=current_year,
            assigned_to=obj.id,
        ).count()

        department_id = obj.department.id if obj.department else None
        personal_reward_points = obj.reward_points_for_current_month

        department_reward_points = (
            Task.objects.filter(
                assigned_to__department=department_id,
                created_at__gte=start_of_month,
                created_at__lt=end_of_month,
            ).aggregate(models.Sum('reward_points'))['reward_points__sum']
            if department_id
            else None
        )

        total_reward_points_in_organization = Task.objects.filter(
            created_at__gte=start_of_month, created_at__lt=end_of_month
        ).aggregate(models.Sum('reward_points'))['reward_points__sum']

        personal_achievements_percentage = (
            (personal_reward_points / total_reward_points_in_organization)
            * 100
            if (
                personal_reward_points is not None
                and total_reward_points_in_organization is not None
                and total_reward_points_in_organization > 0
            )
            else 0
        )

        department_achievements_percentage = (
            (department_reward_points / total_reward_points_in_organization)
            * 100
            if (
                department_reward_points is not None
                and total_reward_points_in_organization is not None
                and total_reward_points_in_organization > 0
            )
            else 0
            if department_id
            else None
        )

        if is_overdue is True or tasks_count == 0:
            progress_for_deadline = 0
        else:
            progress_for_deadline = (today.day / days_in_month) * 100

        return {
            'personal_progress': floor(personal_achievements_percentage),
            'department_progress': floor(department_achievements_percentage)
            if department_achievements_percentage is not None
            else 0,
            'total_reward_points_in_organization': total_reward_points_in_organization  # noqa 501
            if total_reward_points_in_organization is not None
            else 0,
            'progress_for_deadline': round(progress_for_deadline),
        }

    def get_personal_progress(self, obj):
        return self.get_metrics(obj)['personal_progress']

    def get_department_progress(self, obj):
        return self.get_metrics(obj)['department_progress']

    def get_total_reward_points_in_organization(self, obj):
        return self.get_metrics(obj)['total_reward_points_in_organization']

    def get_progress_for_deadline(self, obj):
        return self.get_metrics(obj)['progress_for_deadline']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
