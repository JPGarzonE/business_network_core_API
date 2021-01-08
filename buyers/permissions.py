# Permissions

# Django Rest_framework
from rest_framework.permissions import BasePermission

# Companies permissions
from companies.permissions import IsCompanyMember, IsCompanyMemberWithAdminPermission, IsCompanyMemberWithEditPermission


class IsBuyerMemberWithAdminPermission(IsCompanyMemberWithAdminPermission):
    """Allow access only to users that are members of the company"""

    message = 'You are not a member of the company owner of the buyer data.'


class IsBuyerMemberWithEditPermission(IsCompanyMemberWithEditPermission):
    """Allow access only to users that are members of the company"""

    message = 'You are not a member of the company owner of the buyer data.'


class IsBuyerMember(IsCompanyMember):
    """Allow access only to users that are members of the company"""

    message = 'You are not a member of the company owner of the buyer data.'