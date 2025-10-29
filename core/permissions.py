# core/permissions.py
from rest_framework.permissions import BasePermission

class IsAdminUserCustom(BasePermission):
    """
    Allows access only to authenticated users with role='admin'.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "role", None) == "admin")


class IsTeacherUserCustom(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "teacher"


class IsStudentUserCustom(BasePermission):
    """Allows access only to users with role = 'student'."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"
