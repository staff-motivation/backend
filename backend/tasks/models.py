from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User


class Task(models.Model):
    """
    Модель задачь.
    """
    CREATED = 'created'
    RETURNED = 'returned_for_revision'
    SENT = 'sent_for_review'
    APPROVED = 'approved'
    TASK_STATUSES = (
        (CREATED, _('Created')),
        (RETURNED, _('Returned for revision')),
        (SENT, _('Sent for review')),
        (APPROVED, _('Approved')),
    )

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
    status = models.CharField(
        max_length=21,
        choices=TASK_STATUSES,
        default=CREATED,)
    is_overdue = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Задачу'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return self.title
