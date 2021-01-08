# serializers.py

# Django
from django.conf import settings
from django.contrib.auth import password_validation, authenticate
from django.core.mail import EmailMultiAlternatives
from django.core.validators import RegexValidator
from django.db import transaction
from django.utils import timezone

# Django REST Framework
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

# Models
from ..models import User, Company, CompanyVerification, CompanyMember
from multimedia.models import File

# Serializers
from companies.serializers import CompanyModelSerializer

# Send email
from .verifications import send_company_verification_notification_email

# Utils
from datetime import timedelta
from django.utils.translation import ugettext_lazy as _
import jwt


def generate_user_username(user_full_name):
    """Recieve the name of the user and generate a valid username for it."""
    username_lower = user_full_name.lower()
    generated_username = username_lower.strip().replace(" ", ".")
    i = 0
    while True:
        username = generated_username if i == 0 else generated_username + str(i)
        try:
            User.objects.get( username = username )
        except User.DoesNotExist:
            break
        
        i += 1
    
    return username


class UserModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = (
            'id', 
            'username', 
            'email', 
            'full_name', 
            'is_verified', 
            'is_staff',
        )


class CompanyMember_UserPerspective(serializers.ModelSerializer):

    accountname = serializers.CharField(source = 'company_accountname')
    name = serializers.CharField(source = 'company_name')

    class Meta:
        model = CompanyMember

        fields = (
            'accountname',
            'name'
        )


class CompanyMember_CompanyPerspective(serializers.ModelSerializer):

    username = serializers.CharField(source = 'user_username')
    full_name = serializers.CharField(source = 'user_full_name')
    email = serializers.CharField(source = 'user_email')

    class Meta:
        model = CompanyMember

        fields = (
            'username',
            'fullname',
            'email'
        )


class UserAccessSerializer(serializers.Serializer):
    """Serializer that returns a user information and all the 
    companies data where the user have access. 
    The first company is going to be returned completely and for the 
    others, only is going to be returned its accountname and name"""

    user = UserModelSerializer()

    default_company = CompanyModelSerializer()

    other_companies = CompanyMember_UserPerspective(many = True)


class DocumentationUserSerializer(serializers.Serializer):
    """Serializer created uniquely for display correctly 
    the response data of the Login and signup endpoints"""

    access_token = serializers.CharField()

    access_user = UserAccessSerializer()
    

class UserLoginSerializer(serializers.Serializer):
    """ User Login Serializer

    Handle the login request data.
    """

    email = serializers.EmailField()

    password = serializers.CharField(min_length = 8, max_length = 64)

    def validate(self, data):
        """Check credentials."""
        user = authenticate( username = data['email'], password = data['password'] )

        if not user:
            raise serializers.ValidationError('Invalid credentials')
        
        self.context['user'] = user
        return data

    def create(self, data):
        """Generate or retrieve new token."""
        token, created = Token.objects.get_or_create( user = self.context['user'] )
        return self.context['user'], token.key