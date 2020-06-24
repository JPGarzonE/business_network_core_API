"""User permissions."""

# Django Rest_framework
from rest_framework.permissions import BasePermission

class IsAccountOwner(BasePermission):
    """Allow acces only to objects owned by the requesting user."""

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_account_entity()

        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """Check object and user are the same"""
        return request.user == obj

class IsRelationOwner(BasePermission):
    """Allow access to the account owner of the data."""

    message = "You don't have permission. You're not the owner of the data."

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_object()

        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """Check object and user are the same"""

        return request.user == obj.requester or request.user == obj.addressed

class UserIsVerified(BasePermission):
    """Allow acces to the account that is verified"""

    message = "You can't do this action. You're not verified yet."

    def has_permission(self, request, view):
        """Let object permission grant access."""
        user_entity = view.get_account_entity()

        return user_entity.is_verified