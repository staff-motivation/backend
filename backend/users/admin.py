from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext as _
from django.http import HttpResponse
from django.urls import reverse
from import_export import resources
from django import forms
from django.utils.safestring import mark_safe
from tasks.models import Task

from .models import (
    Achievement, Department, Hardskill, User
)

class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'creator', 'start_date', 'deadline', 'status']
    list_filter = ['status', 'creator']
    search_fields = ['id', 'title', 'description']



class HardskillInline(admin.TabularInline):
    model = User.hardskills.through
    fields = ('hardskill',)
    verbose_name = 'Профессиональный навык'
    verbose_name_plural = 'Профессиональные навыки'
    extra = 1


class HardskillAdmin(admin.ModelAdmin):
    model = Hardskill
    list_display = ('name',)
    search_fields = ('name',)


class AchievementInline(admin.TabularInline):
    model = User.achievements.through
    fields = ('achievement',)
    verbose_name = 'Достижение'
    verbose_name_plural = 'Достижения'
    extra = 1


class AchievementAdmin(admin.ModelAdmin):
    model = Achievement
    list_display = ('get_image', 'name', 'description')
    search_fields = ('name',)

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width=50>")


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = UserCreationForm.Meta.model
        fields = '__all__'
        field_classes = UserCreationForm.Meta.field_classes


class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CustomUserCreationForm
    ordering = ['email']
    list_display = (
        'email', 'is_active', 'is_superuser',
        'role', 'position', 'experience', 'department',
    )
    search_fields = (
        'email', 'is_active',
        'position', 'experience', 'department',
    )
    # filter_vertical = ('department',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name','birthday',
            'position', 'experience', 'department'
        )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'user_permissions', 'role'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')})
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'birthday',
            'position', 'experience', 'department',
        )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'user_permissions', 'role'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    inlines = [HardskillInline, AchievementInline]


admin.site.register(Task, TaskAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Hardskill, HardskillAdmin)
admin.site.register(Achievement, AchievementAdmin)


