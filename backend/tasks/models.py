from django.db import models
from django.utils import timezone
from django.conf import settings


class Task(models.Model):
    title = models.CharField(verbose_name='Заголовок задачи', max_length=255)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Создатель задачи',
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='Назначенные пользователи',
        related_name='assigned_tasks'
    )
    description = models.TextField(verbose_name='Описание задачи')
    creation_date = models.DateTimeField(
        verbose_name='Дата создания задачи',
        default=timezone.now
    )
    start_date = models.DateTimeField(
        verbose_name='Дата начала выполнения задачи',
        null=True,
        blank=True
    )
    deadline = models.DateTimeField(verbose_name='Дедлайн')

    STATUS_CHOICES = [
        ('created', 'Задача создана'),
        ('in_progress', 'В процессе выполнения'),
        ('sent_for_review', 'Отправлена на проверку'),
        ('completed', 'Принята и выполнена'),
        ('returned_for_revision', 'Возвращена на доработку'),
    ]
    status = models.CharField(
        verbose_name='Статус задачи',
        max_length=max(len(choice[0]) for choice in STATUS_CHOICES),
        choices=STATUS_CHOICES,
        default='created'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ('-creation_date',)

    def __str__(self):
        return self.title