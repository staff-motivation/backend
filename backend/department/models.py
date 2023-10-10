from django.db import models
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    BACKEND = 'backend'
    FRONTEND = 'frontend'
    UX_UI = 'ux_ui'
    QA = 'qa'
    OTHER = 'other'
    DEPARTMENT_NAMES = (
        (BACKEND, _('Backend')),
        (FRONTEND, _('Frontend')),
        (UX_UI, _('UX_UI')),
        (QA, _('QA')),
        (OTHER, _('Other')),
    )

    name = models.CharField(
        verbose_name='Подразделение',
        max_length=10,
        choices=DEPARTMENT_NAMES,
        default=OTHER,
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Добавьте описание подразделения',
        blank=True,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Загрузите изображение',
        upload_to='users/department/%Y/%m/%d',
        blank=True,
    )

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'
        ordering = ('name',)

    def __str__(self):
        return str(self.name)
