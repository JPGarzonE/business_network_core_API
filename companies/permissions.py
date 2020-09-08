"""Company permissions."""

# Django Rest_framework
from rest_framework.permissions import BasePermission


class IsCompanyAccountOwner(BasePermission):
    """Allow acces only to account owner by the requesting user."""

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_account_entity()

        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """Check object and user are the same"""
        return request.user == obj.user


class IsDataOwner(BasePermission):
    """Allow access to the account owner of the data."""

    message = "You don't have permission. You're not the owner of the data."

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_object().company

        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """Check object and user are the same"""
        return request.user == obj.user


class IsPredominantEntiyOwner(BasePermission):
    """Allow access to the user owner of the premidominant entity 
    in a through model (Usually that exists because many to many relations)"""

    message = "You don't have permission. You're not the owner of the data."

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_predominant_entity_owner()

        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """Check object and user are the same"""
        return request.user == obj.user


class IsUnregisteredRelationOwner(BasePermission):
    """Allow access to the account owner of the unregistered relation."""

    message = "You don't have permission. You're not the owner of the relationship."

    def has_permission(self, request, view):
        """Let object permission grant access."""
        obj = view.get_object()

        return self.has_object_permission(request, view, obj)

    def has_object_permission(self, request, view, obj):
        """Check object and user are the same"""
        return request.user == obj.requester.user


class UserIsVerified(BasePermission):
    """Allow acces to the account that is verified"""

    message = "You can't do this action. You're not verified yet."

    def has_permission(self, request, view):
        """Let object permission grant access."""
        user_entity = view.get_account_entity().user

        return user_entity.is_verified


class IsCompanyAccountOwnerOrIsVerified(BasePermission):

    message = "You can't do this action. User is not verified yet."

    def has_permission(self, request, view):
        """Let object permission grant access."""
        user_entity = view.get_account_entity().user

        isAccountOwner = (user_entity == request.user)
        isVerified = request.user.is_verified

        return isAccountOwner or isVerified