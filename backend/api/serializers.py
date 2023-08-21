from users.models import User, AllowedEmail
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            "email", "password", "password_confirmation",
            "first_name", "last_name", "birthday"
        ]

    def validate_email(self, value):
        allowed_emails = AllowedEmail.objects.values_list('email', flat=True)
        if value not in allowed_emails:
            raise serializers.ValidationError("Данный email не разрешен для регистрации.")
        return value

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
        return super().validate(data)

    def create(self, validated_data):
        email = validated_data["email"]
        validated_data["username"] = email.split('@')[0]
        return super().create(validated_data)