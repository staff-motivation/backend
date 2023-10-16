from rest_framework import serializers

from department.models import Department
from tasks.models import Task


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


class TaskReviewSerializer(serializers.Serializer):
    review_status = serializers.ChoiceField(
        required=True, choices=[Task.APPROVED, Task.RETURNED]
    )
