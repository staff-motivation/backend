from datetime import date

from core.utils import how_much_time_has_passed
from dateutil.relativedelta import relativedelta  # type: ignore
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.settings import api_settings

from tasks.models import Task
from users.models import Achievement, Contact, Hardskill, User


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('phone', 'telegram', 'github', 'linkedin')


class AchievementSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = Achievement
        fields = '__all__'


class HardskillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hardskill
        fields = ('name',)


class UploadUserImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = ('image',)


class ProgressSerializer(serializers.Serializer):
    personal_progress = serializers.IntegerField()
    department_progress = serializers.IntegerField()


class CustomUserRetrieveSerializer(UserSerializer):
    hardskills = HardskillsSerializer(many=True, required=False)
    achievements = AchievementSerializer(many=True, required=False)
    achievements_read_only = serializers.BooleanField(
        read_only=True, default=False
    )
    reward_points = serializers.IntegerField(read_only=True)
    contacts = ContactSerializer(many=False)
    completed_tasks_count = serializers.IntegerField()
    reward_points_for_current_month = serializers.IntegerField()
    remaining_tasks_count = serializers.SerializerMethodField()
    total_tasks = serializers.SerializerMethodField()
    experience = serializers.SerializerMethodField()
    general_experience = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
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
            'experience',
            'general_experience',
        )

    # def get_contacts(self, obj):
    #     user = self.context['request'].user
    #     # queryset = Contact.objects.filter(user=user.id)
    #     contact = user.contact.get()
    #     return ContactSerializer(contact, many=False).data

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

            Contact.objects.filter(user=instance).update(**contacts_data)

        instance = super().update(instance, validated_data)
        return instance

    def get_experience(self, obj):
        dt = obj.experience
        if dt:
            return how_much_time_has_passed(dt)
        return 'Нет данных'

    def get_general_experience(self, obj):
        dt = obj.general_experience
        if dt:
            return how_much_time_has_passed(dt)
        return 'Нет данных'


class CustomUserCreateSerializer(UserCreateSerializer):
    password_confirmation = serializers.CharField(
        write_only=True, style={'input_type': 'password'}
    )

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ('password_confirmation',)

    def validate(self, data):
        password = data.get('password')
        if len(password) > 30:
            raise serializers.ValidationError(
                'Длина пароля не должна превышать 30 символов.'
            )
        if password != data.get('password_confirmation'):
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
        user = User(**data)
        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {
                    'password': serializer_error[
                        api_settings.NON_FIELD_ERRORS_KEY
                    ]
                }
            ) from e
        return data


class ShortUserProfileSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    reward_points_for_current_month = serializers.IntegerField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'image',
            'role',
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

    def get_department(self, obj):
        return str(self.context['request'].user.department)
