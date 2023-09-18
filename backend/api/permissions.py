from rest_framework import permissions


class IsOrdinaryUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if (
            request.method in permissions.SAFE_METHODS
            or 'POST'
            and view.action == 'send_for_review'
        ):
            return True
        return request.user.is_teamleader


class IsTeamLeader(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_teamleader


class CanEditUserFields(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_teamleader:
            return True
        if request.user.id == obj.id:
            if request.method in permissions.SAFE_METHODS:
                return True
            if 'achievements' in request.data:
                return False
            return True
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
