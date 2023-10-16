from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from tasks.models import Task


class TaskResource(resources.ModelResource):
    """
    Настройки импорта/экспорта для модели Task.
    """

    class Meta:
        model = Task
        skip_unchanged = True
        report_skipped = True


class TaskAdmin(ImportExportModelAdmin):
    """
    Настройки отображения модели Task
    в админ панели.
    """

    list_display = ['id', 'title', 'team_leader', 'deadline', 'status']
    list_filter = ['status', 'team_leader']
    search_fields = ['id', 'title', 'description']
    resource_classes = [TaskResource]


admin.site.register(Task, TaskAdmin)
