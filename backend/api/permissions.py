from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsTeamLeader(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_teamleader


class CanViewAllTasks(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class CanCreateEditDeleteTasks(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_teamleader


class CanEditStatus(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.user.is_teamleader and obj.creator == request.user) or obj.assignees.filter(pk=request.user.pk).exists()


class CanStartTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.assignees.filter(pk=request.user.pk).exists() and obj.status == 'created'


class CanCompleteTask(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_teamleader and obj.status in ['in_progress', 'sent_for_review']


class CanEditUserFields(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_teamleader:
            return True
        if request.user.id == obj.id:
            if request.method in permissions.SAFE_METHODS:
                return True
            if 'achievements' in request.data or 'hardskills' in request.data:
                return False
            return True
        return False


class IsTaskCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user