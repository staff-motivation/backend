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
