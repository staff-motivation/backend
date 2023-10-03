from rest_framework import serializers
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    team_leader = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    status = serializers.CharField(default='created')
    reward_points = serializers.IntegerField(required=True)

    class Meta:
        model = Task
        fields = '__all__'
