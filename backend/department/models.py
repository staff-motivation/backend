from django.db import models
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    BACKEND = 'Backend'
    FRONTEND = 'Frontend'
    UX_UI = 'UX_UI'
    QA = 'QA'
    NONE = 'None'
    DEPARTMENT_NAMES = (
        (BACKEND, _('Backend')),
        (FRONTEND, _('Frontend')),
        (UX_UI, _('UX_UI')),
        (QA, _('QA')),
        (NONE, _('None')),
    )

    name = models.CharField(
        verbose_name='Подразделение',
        max_length=10,
        choices=DEPARTMENT_NAMES,
        default=NONE,
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Добавьте описание подразделения',
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
