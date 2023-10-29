from datetime import datetime

from rest_framework import serializers

from department.models import Department
from tasks.models import Task
from users.models import User


class ChoiceField(serializers.ChoiceField):
    def to_representation(self, obj):
        if obj == '':
            return obj
        return obj.name

    def to_internal_value(self, data):
        if data == '':
            return ''

        for key, _val in self._choices.items():
            if key == data:
                return key
        self.fail('invalid_choice', input=data)


class TaskSerializer(serializers.ModelSerializer):
    team_leader = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    status = serializers.CharField(default='created')
    reward_points = serializers.IntegerField(required=True)
    department = ChoiceField(choices=Department.DEPARTMENT_NAMES)

    class Meta:
        model = Task
        read_only_fields = ('is_overdue',)
        fields = '__all__'


class TaskCreateSerializer(TaskSerializer):
    """[POST] Создание новой задачи."""

    def validate(self, obj):
        department = obj.get('department')
        user = obj.get('assigned_to')
        deadline = obj.get('deadline')
        if deadline < datetime.now(deadline.tzinfo):
            raise serializers.ValidationError(
                {'deadline': 'Дедлайн не может быть в прощедшей дате.'}
            )
        if not User.objects.filter(
            department__name=department, id=user.id
        ).exists():
            raise serializers.ValidationError(
                {'department': 'Такого пользователя нет в этом департаменте.'}
            )
        return obj


class TaskReviewSerializer(serializers.Serializer):
    review_status = serializers.ChoiceField(
        required=True, choices=[Task.APPROVED, Task.RETURNED]
    )
