from department.models import Department
from rest_framework import serializers
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    team_leader = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    status = serializers.CharField(default='created')
    reward_points = serializers.IntegerField(required=True)
    department = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Department.objects.all(),
        allow_null=True,
    )

    class Meta:
        model = Task
        read_only_fields = ('is_overdue',)
        fields = '__all__'


class TaskReviewSerializer(serializers.Serializer):
    review_status = serializers.ChoiceField(
        required=True, choices=[Task.APPROVED, Task.RETURNED]
    )
