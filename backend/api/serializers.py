
from rest_framework import serializers

from notifications.models import Notification


class ProgressSerializer(serializers.Serializer):
    personal_progress = serializers.IntegerField()
    department_progress = serializers.IntegerField()


class ErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
