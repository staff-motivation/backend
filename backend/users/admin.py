from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from tasks.models import Task

from .models import Achievement, Contact, Department, Hardskill, User


class AchievementResource(resources.ModelResource):
    """
    Настройки импорта/экспорта для модели Achievement.
    """

    class Meta:
        model = Achievement
        skip_unchanged = True
        report_skipped = True


class DepartmentResource(resources.ModelResource):
    """
    Настройки импорта/экспорта для модели Department.
    """

    class Meta:
        model = Department
        skip_unchanged = True
        report_skipped = True


class ContactResource(resources.ModelResource):
    """
    Настройки импорта/экспорта для модели Contact.
    """

    class Meta:
        model = Contact
        skip_unchanged = True
        report_skipped = True


class HardskillResource(resources.ModelResource):
    """
    Настройки импорта/экспорта для модели Hardskill.
    """

    class Meta:
        model = Hardskill
        skip_unchanged = True
        report_skipped = True


class UserResource(resources.ModelResource):
    """
    Настройки импорта/экспорта для модели User.
    """

    class Meta:
        model = User
        skip_unchanged = True
        report_skipped = True


class TaskResource(resources.ModelResource):
    """
    Настройки импорта/экспорта для модели Task.
    """

    class Meta:
        model = Task
        skip_unchanged = True
        report_skipped = True


class ContactAdmin(ImportExportModelAdmin):
    """
    Настройки отображения модели Contact
    в админ панели.
    """

    list_display = ('user', 'contact_type', 'link')
    resource_classes = [ContactResource]


class DepartmentAdmin(ImportExportModelAdmin):
    """
    Настройки отображения модели Department
    в админ панели.
    """

    list_display = ('name', 'description', 'image')
    resource_classes = [DepartmentResource]


class TaskAdmin(ImportExportModelAdmin):
    """
    Настройки отображения модели Task
    в админ панели.
    """

    list_display = ['id', 'title', 'team_leader', 'deadline', 'status']
    list_filter = ['status', 'team_leader']
    search_fields = ['id', 'title', 'description']
    resource_classes = [TaskResource]


class HardskillInline(admin.TabularInline):
    """
    Настройки отображения в админ панели
    модели Hardskill для модели User.
    """

    model = User.hardskills.through
    fields = ('hardskill',)
    verbose_name = 'Профессиональный навык'
    verbose_name_plural = 'Профессиональные навыки'
    extra = 1


class HardskillAdmin(ImportExportModelAdmin):
    """
    Настройки отображения модели Hardskill
    в админ панели.
    """

    list_display = ('name',)
    search_fields = ('name',)
    resource_classes = [HardskillResource]


class AchievementInline(admin.TabularInline):
    """
    Настройки отображения в админ панели
    модели Achievement для модели User.
    """

    model = User.achievements.through
    fields = ('achievement',)
    verbose_name = 'Достижение'
    verbose_name_plural = 'Достижения'
    extra = 1


class AchievementAdmin(ImportExportModelAdmin):
    """
    Настройки отображения модели Achievement
    в админ панели.
    """

    list_display = ('get_image', 'name', 'value', 'description')
    search_fields = ('name',)
    resource_classes = [AchievementResource]

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width=50>")


class CustomUserCreationForm(UserCreationForm):
    """
    Настройки кастомной формы создания пользователя
    для модели User. Используется в CustomUserAdmin.
    """

    class Meta:
        model = UserCreationForm.Meta.model
        fields = '__all__'
        field_classes = UserCreationForm.Meta.field_classes


class CustomUserAdmin(ImportExportModelAdmin):
    """
    Настройки отображения модели User
    в админ панели.
    """

    model = User
    add_form = CustomUserCreationForm
    ordering = ['email']
    list_display = (
        'id',
        'email',
        'is_active',
        'is_superuser',
        'role',
        'position',
        'experience',
        'department',
    )
    search_fields = (
        'email',
        'is_active',
        'position',
        'experience',
        'department',
    )
    resource_classes = [UserResource]
    # filter_vertical = ('department',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Personal info'),
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'birthday',
                    'position',
                    'experience',
                    'department',
                )
            },
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'user_permissions',
                    'role',
                ),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),
        (
            _('Personal info'),
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'birthday',
                    'position',
                    'experience',
                    'department',
                )
            },
        ),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'user_permissions',
                    'role',
                ),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    inlines = [HardskillInline, AchievementInline]


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Hardskill, HardskillAdmin)
admin.site.register(Achievement, AchievementAdmin)
admin.site.register(Contact, ContactAdmin)
