from typing import Optional
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rolepermissions.checkers import has_permission


class HasRolePermission(BasePermission):
    required_permission: Optional[str] = None

    def has_permission(self, request, view) -> bool:
        required = getattr(view, 'required_permission', self.required_permission)
        if not required:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return has_permission(user, required)


class IsAdminWriteOrReadOnly(BasePermission):
    """Allow GET/HEAD/OPTIONS to any authenticated user; require 'manage_school' for write ops."""

    def has_permission(self, request, view) -> bool:
        user = request.user
        if request.method in SAFE_METHODS:
            return bool(user and user.is_authenticated)
        # Allow superusers to always write
        if getattr(user, 'is_superuser', False):
            return True
        return bool(user and user.is_authenticated and has_permission(user, 'manage_school'))


