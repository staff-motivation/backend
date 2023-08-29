from rest_framework import permissions

class CanEditOwnData(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Пользователь может редактировать только свои данные
        return request.user == obj

class CanEditSkillsAndAchievements(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Пользователь (или teamleader) может редактировать хардскилы и достижения
        # Самого себя или другого пользователя, но только если он teamleader
        return (
            request.user.is_authenticated and
            (request.user == obj or request.user.is_teamleader)
        )


