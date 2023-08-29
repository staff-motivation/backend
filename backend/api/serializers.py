from users.models import (
    User, CustomUserManager,
    Hardskill, UserHardskill,
    Achievement, UserAchievement
)
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .permissions import CanEditSkillsAndAchievements, CanEditOwnData


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

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'birthday', 'email', 'hardskills', 'achievements')

    def update(self, instance, validated_data):
        can_edit_skills_achievements = CanEditSkillsAndAchievements().has_object_permission(
            self.context['request'], None, instance
        )

        hardskills_data = validated_data.pop('hardskills', [])
        achievements_data = validated_data.pop('achievements', [])

        if can_edit_skills_achievements:
            instance.hardskills.clear()
            instance.achievements.clear()

            for hardskill_data in hardskills_data:
                hardskill, created = Hardskill.objects.get_or_create(name=hardskill_data['name'])
                instance.hardskills.add(hardskill)

            for achievement_data in achievements_data:
                achievement, created = Achievement.objects.get_or_create(
                    name=achievement_data['name'],
                    defaults={'description': achievement_data.get('description', '')}
                )
                instance.achievements.add(achievement)

            instance = super().update(instance, validated_data)

        return instance


class CustomUserCreateSerializer(UserCreateSerializer):
    password_confirmation = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + (
            'password_confirmation', 'birthday'
        )

    def validate(self, data):
        if data["password"] != data.get("password_confirmation"):
            raise serializers.ValidationError("Пароли должны совпадать.")

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")

        required_fields = [
            "email", "password", "password_confirmation",
            "first_name", "last_name", "birthday"
        ]
        if any(field not in data for field in required_fields):
            raise serializers.ValidationError("Не все обязательные поля заполнены.")
        data.pop("password_confirmation")
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user
    