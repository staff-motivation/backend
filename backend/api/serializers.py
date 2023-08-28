from users.models import (
    User, CustomUserManager,
    Hardskill, UserHardskill,
    Achievement, UserAchievement
)
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers


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
    hardskills = HardskillsSerializer(
        many=True,
        required=False
    )
    achievements = AchievementSerializer(
        many=True,
        required=False
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'birthday', 'email', 'hardskills', 'achievements'
        )

    def update(self, instance, validated_data):
        hardskills_data = validated_data.pop('hardskills', [])
        achievements_data = validated_data.pop('achievements', [])
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
    password_confirmation = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    hardskills = HardskillsSerializer(
        many=True,
        required=False
    )
    achievements = AchievementSerializer(
        many=True,
        required=False
    )

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + (
            'password_confirmation', 'birthday', 'hardskills', 'achievements'
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
        if 'hardskills' not in self.initial_data and 'achievements' not in self.initial_data:
            password = validated_data.pop('password')
            user = self.Meta.model(**validated_data)
            user.set_password(password)
            user.save()
            return user
        
        if 'hardskills' in self.initial_data and 'achievements' not in self.initial_data:
            hardskills = validated_data.pop('hardskills')
            password = validated_data.pop('password')
            user = self.Meta.model(**validated_data)
            user.set_password(password)
            user.save()
            for hardskill in hardskills:
                current_hardskill, status = Hardskill.objects.get_or_create(**hardskill)
                UserHardskill.objects.create(
                    hardskill=current_hardskill,
                    user=user
                )
            return user

        if 'achievements' in self.initial_data and 'hardskills' not in self.initial_data:
            achievements = validated_data.pop('achievements')
            password = validated_data.pop('password')
            user = self.Meta.model(**validated_data)
            user.set_password(password)
            user.save()
            for achievement in achievements:
                current_achievement, status = Achievement.objects.get_or_create(**achievement)
                UserAchievement.objects.create(
                    achievement=current_achievement,
                    user=user
                )
            return user
        
        achievements = validated_data.pop('achievements')
        hardskills = validated_data.pop('hardskills')
        password = validated_data.pop('password')
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        for achievement in achievements:
            current_achievement, status = Achievement.objects.get_or_create(**achievement)
            UserAchievement.objects.create(
                achievement=current_achievement,
                user=user
            )
        for hardskill in hardskills:
            current_hardskill, status = Hardskill.objects.get_or_create(**hardskill)
            UserHardskill.objects.create(
                hardskill=current_hardskill,
                user=user
            )
        return user
    