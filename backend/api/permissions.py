from rest_framework import permissions


class CanEditUserFields(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_teamleader:
            return True

        if request.user == obj:
            return request.method in permissions.SAFE_METHODS or request.method in ['PATCH', 'PUT'] and not hasattr(obj, 'achievements') and not hasattr(obj, 'hardskills')

        return request.method in permissions.SAFE_METHODS