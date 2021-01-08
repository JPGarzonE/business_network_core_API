# Permissions

# Django
from django.contrib.auth.models import AnonymousUser

# Django Rest_framework
from rest_framework.permissions import BasePermission

# Models for query the different access
from .models.users import CompanyMember


class IsCompanyMemberWithEditPermission(BasePermission):
    """Allow access only to users that are members of the company"""

    message = 'You are not a member of the company owner of the data.'

    def has_permission(self, request, view):
        """Let object permission grant access."""

        return self.has_object_permission(request, view, None)

    def has_object_permission(self, request, view, obj):
        """Check if user is a member of the company"""
        if type(request.user) is AnonymousUser:
            return False
        
        company = view.get_data_owner_company()

        try:
            CompanyMember.objects.get(
                company = company,
                user = request.user
            )

            return True
        except CompanyMember.DoesNotExist:
            return False


class IsCompanyMemberWithAdminPermission(BasePermission):
    """Allow access only to users that are members of the company"""

    message = 'You are not a member of the company owner of the data.'

    def has_permission(self, request, view):
        """Let object permission grant access."""

        return self.has_object_permission(request, view, None)

    def has_object_permission(self, request, view, obj):
        """Check if user is a member of the company"""
        if type(request.user) is AnonymousUser:
            return False

        company = view.get_data_owner_company()

        try:
            CompanyMember.objects.get(
                company = company,
                user = request.user
            )

            return True
        except CompanyMember.DoesNotExist:
            return False


class IsCompanyMember(BasePermission):
    """Allow access only to users that are members of the company"""

    message = 'You are not a member of the company owner of the data.'

    def has_permission(self, request, view):
        """Let object permission grant access."""

        return self.has_object_permission(request, view, None)

    def has_object_permission(self, request, view, obj):
        """Check if user is a member of the company"""
        if type(request.user) is AnonymousUser:
            return False

        company = view.get_data_owner_company()

        try:
            CompanyMember.objects.get(
                company = company,
                user = request.user
            )

            return True
        except CompanyMember.DoesNotExist:
            return False


class IsVerifiedUser(BasePermission):
    """Allow acces to the account that is verified"""

    message = "You can't do this action. You're not verified yet."

    def has_permission(self, request, view):
        """Let object permission grant access."""
        user_entity = view.get_account_entity()

        return user_entity.is_verified