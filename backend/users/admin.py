from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _


from .models import Department, Bonus, Group, User, UserRating, Membership


class UserRatingInline(admin.TabularInline):
    model = UserRating
    fields = (
        'kpi_name', 'kpi_category',
        'target', 'actual', 'date'
    )
    readonly_fields = (
        'kpi_name', 'kpi_category',
        'target', 'actual', 'date'
    )
    extra = 0


class UserRatingAdmin(admin.ModelAdmin):
    model = UserRating
    list_display = (
        'kpi_name', 'kpi_category',
        'target', 'actual', 'date'
    )
    search_fields = ('kpi_name', 'kpi_category',)


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = UserCreationForm.Meta.model
        fields = '__all__'
        field_classes = UserCreationForm.Meta.field_classes


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CustomUserCreationForm
    list_display = (
        'username', 'email', 'is_active', 'is_superuser',
        'role', 'position', 'experience', 'department',
        'bonus',
    )
    search_fields = (
        'username', 'email', 'is_active',
        'position', 'experience', 'department',
    )
    filter_vertical = ('groups',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'second_name', 'email', 'birthday',
            'position', 'experience', 'department',
            'user_rating', 'contact',
        )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'user_permissions', 'role'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Bonus'), {'fields': ('bonus',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'second_name', 'email', 'birthday',
            'position', 'experience', 'department',
            'user_rating', 'contact',
        )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'user_permissions', 'role'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Bonus'), {'fields': ('bonus',)}),
    )
    inlines = [UserRatingInline]


class CustomUserInline(admin.TabularInline):
    model = User
    fields = (
        'username', 'email', 'role', 'position',
        'experience', 'user_rating_actual',
    )
    readonly_fields = (
        'username', 'email', 'role', 'position',
        'experience', 'user_rating_actual',
    )
    extra = 0

    def user_rating_actual(self, obj):
        return obj.user_rating.actual
    user_rating_actual.short_description = 'Актульный KPI работника'


class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    list_display = ('name', 'user_count')
    inlines = [CustomUserInline]

    def user_count(self, obj):
        return obj.users_department.count()

    user_count.short_description = 'Колличество участников'


class GroupAdmin(admin.ModelAdmin):
    model = Group
    list_display = ('name',)


class BonusAdmin(admin.ModelAdmin):
    model = Bonus
    list_display = ('bonus_points', 'privilege')


admin.site.register(Bonus, BonusAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserRating, UserRatingAdmin)
admin.site.register(Membership)
