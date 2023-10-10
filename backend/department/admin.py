from department.models import Department
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class DepartmentResource(resources.ModelResource):
    """
    Настройки импорта/экспорта для модели Department.
    """

    class Meta:
        model = Department
        skip_unchanged = True
        report_skipped = True


class DepartmentAdmin(ImportExportModelAdmin):
    """
    Настройки отображения модели Department
    в админ панели.
    """

    list_display = ('name', 'description', 'image')
    resource_classes = [DepartmentResource]


admin.site.register(Department, DepartmentAdmin)
