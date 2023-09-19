from datetime import date

from dateutil.relativedelta import relativedelta  # type: ignore
from django.db import models
from djoser.serializers import UserCreateSerializer, UserSerializer
from notifications.models import Notification
from rest_framework import serializers
from tasks.models import Task
from users.models import Achievement, Contact, Hardskill, User


class ProgressUserAndDepartmentSerializer(serializers.ModelSerializer):
    personal_progress = serializers.SerializerMethodField()
    department_progress = serializers.SerializerMethodField()
    total_reward_points_in_organization = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'personal_progress',
            'department_progress',
            'total_reward_points_in_organization',
        ]

    def get_metrics(self, obj):
        today = date.today()
        start_of_month = today.replace(day=1)
        end_of_month = today + relativedelta(
            day=31, hour=23, minute=59, second=59, microsecond=999999
        )

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

        return {
            'personal_progress': round(personal_achievements_percentage, 2),
            'department_progress': round(department_achievements_percentage, 2)
            if department_achievements_percentage is not None
            else 0,
            'total_reward_points_in_organization': total_reward_points_in_organization  # noqa 501
            if total_reward_points_in_organization is not None
            else 0,
        }

    def get_personal_progress(self, obj):
        return self.get_metrics(obj)['personal_progress']

    def get_department_progress(self, obj):
        return self.get_metrics(obj)['department_progress']

    def get_total_reward_points_in_organization(self, obj):
        return self.get_metrics(obj)['total_reward_points_in_organization']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('contact_type', 'link')


class AchievementSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = Achievement
        fields = ('name', 'value', 'image', 'description')


class HardskillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hardskill
        fields = ('name',)


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('image',)


class CustomUserRetrieveSerializer(UserSerializer):
    hardskills = HardskillsSerializer(many=True, required=False)
    achievements = AchievementSerializer(many=True, required=False)
    achievements_read_only = serializers.BooleanField(
        read_only=True, default=False
    )
    reward_points = serializers.IntegerField(read_only=True)
    contacts = ContactSerializer(many=True, required=False)
    completed_tasks_count = serializers.IntegerField()
    reward_points_for_current_month = serializers.IntegerField()
    remaining_tasks_count = serializers.SerializerMethodField()
    total_tasks = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'birthday',
            'email',
            'hardskills',
            'achievements',
            'role',
            'position',
            'achievements_read_only',
            'reward_points',
            'contacts',
            'completed_tasks_count',
            'reward_points_for_current_month',
            'remaining_tasks_count',
            'total_tasks',
        )

    def get_total_tasks(self, instance):
        today = date.today()
        start_of_month = today.replace(day=1)
        end_of_month = today + relativedelta(day=31)
        total_tasks = Task.objects.filter(
            assigned_to=instance,
            created_at__gte=start_of_month,
            created_at__lte=end_of_month,
        ).count()
        return total_tasks

    def get_remaining_tasks_count(self, obj):
        today = date.today()
        start_of_month = today.replace(day=1)
        end_of_month = today + relativedelta(day=31)

        total_tasks = Task.objects.filter(
            assigned_to=obj,
            created_at__gte=start_of_month,
            created_at__lte=end_of_month,
        ).count()

        return total_tasks - obj.completed_tasks_count

    def update(self, instance, validated_data):
        hardskills_data = validated_data.pop('hardskills', [])
        achievements_data = validated_data.pop('achievements', [])
        contacts_data = validated_data.pop('contacts', [])
        is_teamleader = self.context['request'].user.is_teamleader
        is_user_self = instance == self.context['request'].user

        if is_teamleader:
            instance.achievements.clear()
            for achievement_data in achievements_data:
                achievement, created = Achievement.objects.get_or_create(
                    name=achievement_data['name'],
                    defaults={
                        'description': achievement_data.get('description', '')
                    },
                )
                instance.achievements.add(achievement)

        if is_user_self:
            instance.hardskills.clear()
            for hardskill_data in hardskills_data:
                hardskill, created = Hardskill.objects.get_or_create(
                    name=hardskill_data['name']
                )
                instance.hardskills.add(hardskill)

            for contact_data in contacts_data:
                contact_type = contact_data.get('contact_type')
                link = contact_data.get('link')
                if contact_type and link:
                    contact, created = Contact.objects.update_or_create(
                        user=instance,
                        contact_type=contact_type,
                        defaults={'link': link},
                    )
        instance = super().update(instance, validated_data)
        return instance


class CustomUserCreateSerializer(UserCreateSerializer):
    password_confirmation = serializers.CharField(
        write_only=True, style={'input_type': 'password'}
    )

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ('password_confirmation',)

    def validate(self, data):
        if data['password'] != data.get('password_confirmation'):
            raise serializers.ValidationError('Пароли должны совпадать.')

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )

        required_fields = [
            'email',
            'password',
            'password_confirmation',
            'first_name',
            'last_name',
        ]
        if any(field not in data for field in required_fields):
            raise serializers.ValidationError(
                'Не все обязательные поля заполнены.'
            )
        data.pop('password_confirmation')
        return data


class TaskSerializer(serializers.ModelSerializer):
    team_leader = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    status = serializers.CharField(default='created')
    reward_points = serializers.IntegerField(required=True)

    class Meta:
        model = Task
        fields = '__all__'


class ShortUserProfileSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    reward_points_for_current_month = (
        serializers.IntegerField()
    )  # Добавьте это поле

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'image',
            'reward_points',
            'rating',
            'department',
            'reward_points_for_current_month',
        )

    def get_rating(self, obj):
        users = User.objects.filter(is_active=True).order_by(
            '-reward_points', 'email'
        )
        user_ids = [user.id for user in users]
        rating = user_ids.index(obj.id) + 1
        return rating
