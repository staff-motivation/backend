from users.models import User, CustomUserManager, Hardskill, UserHardskill
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers


class HardskillsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hardskill
        fields = ('name',)


class CustomUserCreateSerializer(UserCreateSerializer):
    password_confirmation = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    hardskills = HardskillsSerializer(
        many=True,
        required=False
    )

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ('password_confirmation', 'birthday', 'hardskills')

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
        if 'hardskills' not in self.initial_data:
            password = validated_data.pop('password')
            user = self.Meta.model(**validated_data)
            user.set_password(password)
            user.save()
            return user
        
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
    