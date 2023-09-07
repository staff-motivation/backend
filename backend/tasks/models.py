from django.db import models
from users.models import User


STATUS_CHOICES = [
    ('created', 'Задача создана'),
    ('in_progress', 'В процессе выполнения'),
    ('sent_for_review', 'Отправлена на проверку'),
    ('completed', 'Принята и выполнена'),
    ('returned_for_revision', 'Возвращена на доработку'),
]


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    reward_points = models.PositiveIntegerField(default=0)
    team_leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_created')
    assigned_to = models.ManyToManyField(User, related_name='assigned_tasks', blank=True)
    status = models.CharField(max_length=21, choices=STATUS_CHOICES)

    def __str__(self):
        return self.title


class TaskUpdate(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='updates')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    update_text = models.TextField()
    status = models.CharField(max_length=21, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update for {self.task.title}"


class TaskInvitation(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Invitation for {self.user.first_name} to task {self.task.title}"