from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _


from .models import Department, User


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = UserCreationForm.Meta.model
        fields = '__all__'
        field_classes = UserCreationForm.Meta.field_classes


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CustomUserCreationForm
    list_display = (
        'username', 'email',
        'is_active', 'is_superuser',
        'role', 'position', 'experience', 'department',
    )
    search_fields = (
        'username', 'email', 'is_active',
        'position', 'experience', 'department',
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name',
            'second_name', 'email', 'birthday',
            'position', 'experience', 'department',
            'contact',
        )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',
                       'user_permissions', 'role'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name',
            'second_name', 'email', 'birthday',
            'position', 'experience', 'department',
            'contact',
        )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',
                       'user_permissions', 'role'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'department':
            kwargs['queryset'] = Department.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CustomUserInline(admin.TabularInline):
    model = User
    fields = ('username', 'email',
              'role', 'position', 'experience')
    readonly_fields = ('username', 'email',
                       'role', 'position', 'experience')
    extra = 0


class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    list_display = ('name', 'user_count')
    inlines = [CustomUserInline]

    def user_count(self, obj):
        return obj.users_department.count()

    user_count.short_description = 'Колличество участников'


admin.site.register(Department, DepartmentAdmin)
admin.site.register(User, CustomUserAdmin)
