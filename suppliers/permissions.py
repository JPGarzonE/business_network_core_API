# Permissions

# Django Rest_framework
from rest_framework.permissions import BasePermission

# Companies permissions
from companies.permissions import IsCompanyMember, IsCompanyMemberWithAdminPermission, IsCompanyMemberWithEditPermission


class IsSupplierMemberWithAdminPermission(IsCompanyMemberWithAdminPermission):
    """Allow access only to users that are members of the company"""

    message = 'You are not a member of the company owner of the supplier data.'


class IsSupplierMemberWithEditPermission(IsCompanyMemberWithEditPermission):
    """Allow access only to users that are members of the company"""

    message = 'You are not a member of the company owner of the supplier data.'


class IsSupplierMember(IsCompanyMember):
    """Allow access only to users that are members of the company"""

    message = 'You are not a member of the company owner of the supplier data.'