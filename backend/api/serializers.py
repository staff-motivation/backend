from users.models import User
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers


class CustomUserCreateSerializer(UserCreateSerializer):
    password_confirmation = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            "username", "email", "password", "password_confirmation",
            "first_name", "last_name", "birthday", "second_name"
        ]

    def validate(self, data):
        if data["password"] != data.get("password_confirmation"):
            raise serializers.ValidationError("Пароли должны совпадать.")

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")

        required_fields = [
            "username", "email", "password", "password_confirmation",
            "first_name", "last_name", "birthday", "second_name"
        ]
        if any(field not in data for field in required_fields):
            raise serializers.ValidationError("Не все обязательные поля заполнены.")
        data.pop("password_confirmation")
        return super().validate(data)

    def create(self, validated_data):
        return super().create(validated_data)