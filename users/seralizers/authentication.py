# Serializers authentication

# Django
from django.contrib.auth import authenticate

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token

# Serializers
from .users import UserModelSerializer
from .tokens import AuthenticationTokensResponseSerializer
from companies.serializers.companies import CompanyModelSerializer
from companies.serializers.members import CompanyMember_UserPerspective


class UserIdentitySerializer(serializers.Serializer):
    """
    Serializer that returns the identity of a user.\n 
    It contains the user main info and the data of all the 
    companies where it have access. The first company is going 
    to be returned completely and for the others, only is 
    going to be returned its accountname and name.
    """

    user = UserModelSerializer()

    access_company = CompanyModelSerializer()

    other_companies = CompanyMember_UserPerspective(many = True)


class LoginAccessSerializer(serializers.Serializer):
    """
    Serializer that returns the access data of a user after a login.\n
    It returns the tokens for authorize its transactions,
    the user data and the companies it has access (One or more).
    A default complete company and an overview of the other ones.
    """

    tokens = AuthenticationTokensResponseSerializer()

    user = UserModelSerializer()

    access_company = CompanyModelSerializer()

    other_companies = CompanyMember_UserPerspective(many = True)