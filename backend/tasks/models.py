from django.db import models
from django.conf import settings
import datetime


class TaskStatus(models.TextChoices):
    """ Task status"""
    TASK_CLOSED = 'Задача завершена'
    TASK_DELEGATED = 'Задача назначена'
    TASK_ACCEPTED = 'Задача принята исполнителем'
    TASK_FINISHED = 'Задача выполнена исполнителем'
    __empty__ = _('(Статус задачи не определён)')
# Необходимо разграничивать выставление статуса в зависимости от роли


class Task(models.Model):
    """Task model"""
    task_title = models.TextField(
        verbose_name='Название задачи'
    )
    team_lead_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_DEFAULT,
        null=True,
        default='deleted_user',
        related_name='delegated_tasks'
    )

    employee_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_DEFAULT,
        null=True,
        default='deleted_user',
        related_name='accepted_tasks'
    )
    task_description = models.TextField(
        verbose_name='Описание задачи'
    )
    task_date_start = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата назначения задачи'
    )
    task_date_finish = models.DateField(
        verbose_name='Плановая дата завершения задачи'
    )

    task_status = models.CharField(
        verbose_name='Текущий статус задачи',
        max_length=max(len(_[0]) for _ in TaskStatus.choices),
        choices=TaskStatus.choices,
    )

    @property
    def is_expired(self):
        """проверяем. что событие не просрочено"""
        return datetime.date.today() > self.task_date_finish

    # для проверки статуса:
    #
    # task = Task.objects.first()
    #
    # if task.is_expired:
    # do something
