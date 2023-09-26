from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    reward_points = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    team_leader = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks_created'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        blank=False,
    )
    status = models.CharField(max_length=21, default='created')
    is_overdue = models.BooleanField(default=False)

    def __str__(self):
        return self.title
