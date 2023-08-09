from users.models import User
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers


class CustomUserCreateSerializer(UserCreateSerializer):
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username", "email", "password", "password_confirmation",
            "first_name", "last_name", "birthday", "second_name"
        ]

    def validate(self, data):
        if data["password"] != data.get("password_confirmation"):
            raise serializers.ValidationError("Пароли должны совпадать.")
        return data

    def create(self, validated_data):
        default_position = User._meta.get_field("position").default
        default_experience = User._meta.get_field("experience").default
        validated_data.setdefault("position", default_position)
        validated_data.setdefault("experience", default_experience)

        return super().create(validated_data)