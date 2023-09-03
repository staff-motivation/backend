from users.models import (
    User, CustomUserManager,
    Hardskill, UserHardskill,
    Achievement, UserAchievement
)
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, permissions
from tasks.models import Task, TaskUpdate, TaskInvitation
from .permissions import CanEditUserFields
from rest_framework.exceptions import PermissionDenied


class AchievementSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = Achievement
        fields = ('name', 'image', 'description')


class HardskillsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hardskill
        fields = ('name',)


class CustomUserRetrieveSerializer(UserSerializer):
    hardskills = HardskillsSerializer(many=True, required=False)
    achievements = AchievementSerializer(many=True, required=False)
    hardskills_read_only = serializers.BooleanField(read_only=True, default=False)
    achievements_read_only = serializers.BooleanField(read_only=True, default=False)
    reward_points = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('first_name',
                  'last_name',
                  'birthday',
                  'email',
                  'hardskills',
                  'achievements',
                  'role',
                  'position',
                  'hardskills_read_only',
                  'achievements_read_only',
                  'reward_points')

    def update(self, instance, validated_data):
        hardskills_data = validated_data.pop('hardskills', [])
        achievements_data = validated_data.pop('achievements', [])

        if self.context['request'].user.is_teamleader:
            instance.hardskills.clear()
            instance.achievements.clear()

            for hardskill_data in hardskills_data:
                hardskill, created = Hardskill.objects.get_or_create(
                    name=hardskill_data['name'])
                instance.hardskills.add(hardskill)

            for achievement_data in achievements_data:
                achievement, created = Achievement.objects.get_or_create(
                    name=achievement_data['name'],
                    defaults={'description': achievement_data.get('description', '')}
                )
                instance.achievements.add(achievement)
        else:
            validated_data['hardskills_read_only'] = instance.hardskills.all()
            validated_data['achievements_read_only'] = instance.achievements.all()

        instance = super().update(instance, validated_data)
        return instance


class CustomUserCreateSerializer(UserCreateSerializer):
    password_confirmation = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'})

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + (
            'password_confirmation',
        )

    def validate(self, data):
        if data["password"] != data.get("password_confirmation"):
            raise serializers.ValidationError("Пароли должны совпадать.")

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")

        required_fields = [
            "email", "password", "password_confirmation",
            "first_name", "last_name"
        ]
        if any(field not in data for field in required_fields):
            raise serializers.ValidationError("Не все обязательные поля заполнены.")
        data.pop("password_confirmation")
        return data


class TaskSerializer(serializers.ModelSerializer):
    team_leader = serializers.HiddenField(default=serializers.CurrentUserDefault())
    status = serializers.CharField(default='created')

    class Meta:
        model = Task
        fields = '__all__'


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskUpdate
        fields = '__all__'


class TaskInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskInvitation
        fields = '__all__'